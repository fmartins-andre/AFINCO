"""
Relatório de Receitas — Escriba Document — modo janela.

Abre uma janela para escolher o período e gerar o TXT. Se o config.ini
não existir, abre antes a tela de configuração do banco, que testa a
conexão e cria o arquivo.
"""
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import font, messagebox, ttk

import rd_document as rd

TITULO = 'Relatório de Receitas — Document'
COR_ERRO = '#b00020'
COR_OK = '#1b5e20'
COR_INFO = '#555555'


class Andamento:
    """
    Barra de progresso + etapa atual + tempo decorrido, para mostrar
    enquanto o banco processa.
    """

    def __init__(self, pai, linha, largura=340):
        self.quadro = ttk.Frame(pai)
        self.quadro.grid(row=linha, column=0, columnspan=2, sticky='we', pady=(12, 0))
        self.quadro.grid_remove()
        self.barra = ttk.Progressbar(self.quadro, mode='indeterminate', length=largura)
        self.barra.pack(fill='x')
        self.texto = ttk.Label(self.quadro, text='', foreground=COR_INFO)
        self.texto.pack(anchor='w', pady=(4, 0))
        self.etapa = ''
        self.inicio = None

    def iniciar(self, etapa):
        self.etapa = etapa
        self.inicio = time.monotonic()
        self.quadro.grid()
        self.barra.start(12)
        self._atualizar()

    def avancar(self, etapa):
        self.etapa = etapa

    def parar(self):
        self.inicio = None
        self.barra.stop()
        self.quadro.grid_remove()

    def _atualizar(self):
        if self.inicio is None:
            return
        decorrido = rd.formatar_tempo(time.monotonic() - self.inicio)
        self.texto.config(text=f'{self.etapa}   {decorrido}')
        self.quadro.after(100, self._atualizar)


def em_segundo_plano(janela, tarefa, ao_avancar, ao_terminar):
    """
    Roda `tarefa(avisar)` numa thread (para a janela não travar).
    Cada `avisar(etapa)` chega em `ao_avancar(etapa)` e o fim em
    `ao_terminar(resultado, erro)`, ambos na thread da interface.
    """
    fila = queue.Queue()

    def trabalho():
        try:
            fila.put(('fim', tarefa(lambda etapa: fila.put(('etapa', etapa, None))), None))
        except Exception as e:  # repassado para a interface
            fila.put(('fim', None, e))

    def verificar():
        try:
            while True:
                tipo, valor, erro = fila.get_nowait()
                if tipo == 'etapa':
                    ao_avancar(valor)
                else:
                    ao_terminar(valor, erro)
                    return
        except queue.Empty:
            if janela.winfo_exists():
                janela.after(100, verificar)

    threading.Thread(target=trabalho, daemon=True).start()
    janela.after(100, verificar)


def mostrar_erro(janela, erro):
    if isinstance(erro, rd.ConsultaDemorada):
        if messagebox.askyesno(
            TITULO, f'{erro}\n\nDeseja abrir a pasta do arquivo de diagnóstico?', icon='warning', parent=janela,
        ):
            abrir_pasta(erro.diagnostico.parent)
    elif isinstance(erro, rd.ErroRelatorio):
        rd.log.error('%s', erro)
        messagebox.showerror(TITULO, str(erro), parent=janela)
    else:
        rd.log.error('Erro inesperado', exc_info=erro)
        messagebox.showerror(
            TITULO, f'Erro inesperado: {erro}\n\nOs detalhes foram gravados em relatorio.log.', parent=janela,
        )


def abrir_pasta(pasta):
    if sys.platform == 'win32':
        os.startfile(pasta)
        return
    # O executável do PyInstaller troca o LD_LIBRARY_PATH pelas bibliotecas
    # embutidas; programas do sistema (xdg-open, gerenciador de arquivos)
    # precisam do ambiente original para não falhar.
    ambiente = dict(os.environ)
    if getattr(sys, 'frozen', False):
        original = ambiente.pop('LD_LIBRARY_PATH_ORIG', None)
        if original is None:
            ambiente.pop('LD_LIBRARY_PATH', None)
        else:
            ambiente['LD_LIBRARY_PATH'] = original
    subprocess.Popen(['xdg-open', str(pasta)], env=ambiente)


class VisualizadorRelatorio(tk.Toplevel):
    """
    Mostra o TXT gerado, somente leitura (o arquivo contábil não pode ser
    alterado sem querer), com fonte de largura fixa e botão de copiar tudo.
    """

    def __init__(self, pai, resultado):
        super().__init__(pai)
        self.resultado = resultado
        self.title(f'Relatório gerado — {resultado.arquivo.name}')
        self.minsize(560, 300)

        # o arquivo usa CRLF; o \r apareceria como símbolo no widget
        texto = resultado.arquivo.read_text(encoding='ascii').replace('\r\n', '\n')

        topo = ttk.Frame(self, padding=(12, 12, 12, 6))
        topo.pack(fill='x')
        ttk.Label(topo, text=rd.formatar_resumo(resultado), justify='left').pack(anchor='w')

        quadro = ttk.Frame(self, padding=(12, 0))
        quadro.pack(fill='both', expand=True)
        self.texto = tk.Text(
            quadro, wrap='none', width=84, height=24, font=font.nametofont('TkFixedFont'),
            undo=False, borderwidth=1, relief='solid',
        )
        rolagem_v = ttk.Scrollbar(quadro, orient='vertical', command=self.texto.yview)
        rolagem_h = ttk.Scrollbar(quadro, orient='horizontal', command=self.texto.xview)
        self.texto.configure(yscrollcommand=rolagem_v.set, xscrollcommand=rolagem_h.set)
        self.texto.grid(row=0, column=0, sticky='nsew')
        rolagem_v.grid(row=0, column=1, sticky='ns')
        rolagem_h.grid(row=1, column=0, sticky='we')
        quadro.rowconfigure(0, weight=1)
        quadro.columnconfigure(0, weight=1)

        self.texto.insert('1.0', texto)
        self.texto.configure(state='disabled')  # somente leitura; seleção e Ctrl+C continuam funcionando

        botoes = ttk.Frame(self, padding=12)
        botoes.pack(fill='x')
        self.botao_copiar = ttk.Button(botoes, text='Copiar todo o texto', command=self.copiar)
        self.botao_copiar.pack(side='left')
        ttk.Button(botoes, text='Abrir pasta', command=lambda: abrir_pasta(resultado.arquivo.parent)).pack(
            side='left', padx=(6, 0))
        self.aviso = ttk.Label(botoes, text='', foreground=COR_OK)
        self.aviso.pack(side='left', padx=(12, 0))
        ttk.Button(botoes, text='Fechar', command=self.destroy).pack(side='right')

        self.bind('<Escape>', lambda _: self.destroy())
        self.focus_set()

    def copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.texto.get('1.0', 'end-1c'))
        self.update()  # entrega o conteúdo à área de transferência do sistema
        self.aviso.config(text=f'✔ {self.resultado.linhas} linhas copiadas')
        self.after(3000, lambda: self.aviso.winfo_exists() and self.aviso.config(text=''))


class TelaBanco(tk.Toplevel):
    """Pede os dados do banco, testa a conexão e grava no config.ini."""

    def __init__(self, pai, arquivo):
        super().__init__(pai)
        self.arquivo = arquivo
        self.salvou = False
        self.ocupado = False
        self.title('Configurar banco de dados')
        self.resizable(False, False)
        self.transient(pai)
        self.protocol('WM_DELETE_WINDOW', self.fechar)

        atual = rd.ler_banco(arquivo) if arquivo.exists() else {}
        self.campos = {}
        quadro = ttk.Frame(self, padding=16)
        quadro.grid()
        ttk.Label(
            quadro, text='Informe os dados de acesso ao servidor do Escriba.', wraplength=320,
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))

        for i, (chave, rotulo, padrao) in enumerate([
            ('host', 'Servidor (IP ou nome):', ''),
            ('porta', 'Porta:', '3306'),
            ('usuario', 'Usuário:', ''),
            ('senha', 'Senha:', ''),
        ], start=1):
            ttk.Label(quadro, text=rotulo).grid(row=i, column=0, sticky='w', pady=3)
            campo = ttk.Entry(quadro, width=28, show='•' if chave == 'senha' else '')
            campo.insert(0, atual.get(chave) or padrao)
            campo.grid(row=i, column=1, sticky='we', pady=3, padx=(8, 0))
            self.campos[chave] = campo

        self.andamento = Andamento(quadro, 5, largura=300)

        botoes = ttk.Frame(quadro)
        botoes.grid(row=6, column=0, columnspan=2, sticky='e', pady=(12, 0))
        self.botao_salvar = ttk.Button(botoes, text='Testar e salvar', command=self.testar)
        self.botao_salvar.grid(row=0, column=0, padx=(0, 6))
        self.botao_cancelar = ttk.Button(botoes, text='Cancelar', command=self.fechar)
        self.botao_cancelar.grid(row=0, column=1)

        self.bind('<Return>', lambda _: self.testar())
        self.campos['host'].focus_set()
        self.grab_set()

    def fechar(self):
        if not self.ocupado:  # espera o teste em andamento terminar
            self.destroy()

    def testar(self):
        if self.ocupado:
            return
        dados = {k: c.get() for k, c in self.campos.items()}
        self.ocupado = True
        for botao in (self.botao_salvar, self.botao_cancelar):
            botao.state(['disabled'])
        self.andamento.iniciar('Testando a conexão com o banco...')

        def ao_terminar(_, erro):
            self.ocupado = False
            self.andamento.parar()
            for botao in (self.botao_salvar, self.botao_cancelar):
                botao.state(['!disabled'])
            if erro:
                return mostrar_erro(self, erro)
            rd.salvar_banco(self.arquivo, **dados)
            self.salvou = True
            messagebox.showinfo(TITULO, 'Conexão OK. Configuração salva.', parent=self)
            self.destroy()

        em_segundo_plano(self, lambda _: rd.testar_conexao(**dados), self.andamento.avancar, ao_terminar)


class Aplicativo(tk.Tk):
    def __init__(self, arquivo_config):
        super().__init__()
        self.arquivo = arquivo_config
        self.resultado = None
        self.ocupado = False
        self.title(TITULO)
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.fechar)

        quadro = ttk.Frame(self, padding=20)
        quadro.grid()

        ttk.Label(quadro, text='Relatório de Receitas', font=('', 13, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(quadro, text='Escriba Document — Títulos e Documentos, PJ e Certidões', foreground=COR_INFO).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 14))

        ini, fim = rd.mes_anterior()
        self.data_ini = self._campo_data(quadro, 2, 'Data inicial:', ini)
        self.data_fim = self._campo_data(quadro, 3, 'Data final:', fim)

        self.botao_gerar = ttk.Button(quadro, text='Gerar relatório', command=self.gerar)
        self.botao_gerar.grid(row=4, column=0, columnspan=2, sticky='we', pady=(14, 0), ipady=4)

        self.andamento = Andamento(quadro, 5)

        self.status = ttk.Label(quadro, text='', wraplength=340, justify='left')
        self.status.grid(row=6, column=0, columnspan=2, sticky='w', pady=(12, 0))

        rodape = ttk.Frame(quadro)
        rodape.grid(row=7, column=0, columnspan=2, sticky='we', pady=(12, 0))
        self.botao_ver = ttk.Button(rodape, text='Ver relatório', command=self.ver_relatorio)
        self.botao_pasta = ttk.Button(rodape, text='Abrir pasta', command=self.abrir_pasta)
        self.botao_config = ttk.Button(rodape, text='Configurar banco...', command=self.configurar)
        self.botao_config.pack(side='right')

        self.bind('<Return>', lambda _: self.gerar())
        if not self.arquivo.exists():
            self.after(200, self.configurar)

    def _campo_data(self, quadro, linha, rotulo, valor):
        ttk.Label(quadro, text=rotulo).grid(row=linha, column=0, sticky='w', pady=3)
        campo = ttk.Entry(quadro, width=14, justify='center')
        campo.insert(0, f'{valor:%d/%m/%Y}')
        campo.grid(row=linha, column=1, sticky='w', pady=3, padx=(8, 0))
        return campo

    def fechar(self):
        if self.ocupado and not messagebox.askyesno(
            TITULO, 'O relatório ainda está sendo gerado. Deseja sair mesmo assim?', parent=self,
        ):
            return
        self.destroy()

    def configurar(self):
        if self.ocupado:
            return False
        tela = TelaBanco(self, self.arquivo)
        self.wait_window(tela)
        return tela.salvou

    def ocupar(self, ocupado):
        self.ocupado = ocupado
        estado = ['disabled'] if ocupado else ['!disabled']
        for widget in (self.botao_gerar, self.botao_config, self.data_ini, self.data_fim):
            widget.state(estado)

    def gerar(self):
        if self.ocupado:
            return
        try:
            config = rd.carregar_config(self.arquivo)
        except rd.ConfigAusente:
            if self.configurar():
                self.gerar()
            return
        except rd.ErroRelatorio as e:
            return mostrar_erro(self, e)

        try:
            data_ini = rd.ler_data(self.data_ini.get())
            data_fim = rd.ler_data(self.data_fim.get())
        except rd.ErroRelatorio as e:
            return mostrar_erro(self, e)
        if data_fim < data_ini:
            return mostrar_erro(self, rd.ErroRelatorio('A data final é anterior à data inicial.'))

        arquivo_txt = rd.arquivo_saida(config, data_ini, data_fim)
        if arquivo_txt.exists() and not messagebox.askyesno(
            TITULO, f'O arquivo {arquivo_txt.name} já existe.\nDeseja substituí-lo?', parent=self,
        ):
            return

        self.ocupar(True)
        self.botao_ver.pack_forget()
        self.botao_pasta.pack_forget()
        self.status.config(text='')
        self.andamento.iniciar('Preparando...')

        def ao_terminar(resultado, erro):
            self.ocupar(False)
            self.andamento.parar()
            if erro:
                self.status.config(text='✖ O relatório não foi gerado.', foreground=COR_ERRO)
                return mostrar_erro(self, erro)
            self.resultado = resultado
            self.status.config(text='✔ ' + rd.formatar_resumo(resultado), foreground=COR_OK)
            self.botao_ver.pack(side='left')
            self.botao_pasta.pack(side='left', padx=(6, 0))
            self.ver_relatorio()  # abre o relatório logo após salvar

        em_segundo_plano(
            self, lambda avisar: rd.gerar(config, data_ini, data_fim, avisar), self.andamento.avancar, ao_terminar,
        )

    def ver_relatorio(self):
        if not self.resultado:
            return
        try:
            VisualizadorRelatorio(self, self.resultado)
        except OSError as e:
            mostrar_erro(self, rd.ErroRelatorio(f'Não foi possível abrir {self.resultado.arquivo}.\n\nDetalhe: {e}'))

    def abrir_pasta(self):
        if self.resultado:
            abrir_pasta(self.resultado.arquivo.parent)


def main():
    arquivo = rd.pasta_do_programa() / rd.CONFIG_NOME
    rd.configurar_log(arquivo.parent)
    Aplicativo(arquivo).mainloop()


if __name__ == '__main__':
    main()
