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
import tkinter as tk
from tkinter import messagebox, ttk

import rd_document as rd

TITULO = 'Relatório de Receitas — Document'


def em_segundo_plano(raiz, tarefa, ao_terminar):
    """
    Roda `tarefa` numa thread (para a janela não travar) e chama
    `ao_terminar(resultado, erro)` de volta na thread da interface.
    """
    fila = queue.Queue()

    def trabalho():
        try:
            fila.put((tarefa(), None))
        except Exception as e:  # repassado para a interface
            fila.put((None, e))

    def verificar():
        try:
            resultado, erro = fila.get_nowait()
        except queue.Empty:
            raiz.after(100, verificar)
        else:
            ao_terminar(resultado, erro)

    threading.Thread(target=trabalho, daemon=True).start()
    raiz.after(100, verificar)


def mostrar_erro(janela, erro):
    if isinstance(erro, rd.ErroRelatorio):
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
    else:
        subprocess.Popen(['xdg-open', str(pasta)])


class TelaBanco(tk.Toplevel):
    """Pede os dados do banco, testa a conexão e grava no config.ini."""

    def __init__(self, pai, arquivo):
        super().__init__(pai)
        self.arquivo = arquivo
        self.salvou = False
        self.title('Configurar banco de dados')
        self.resizable(False, False)
        self.transient(pai)

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

        self.status = ttk.Label(quadro, text='', foreground='#555')
        self.status.grid(row=5, column=0, columnspan=2, sticky='w', pady=(10, 0))

        botoes = ttk.Frame(quadro)
        botoes.grid(row=6, column=0, columnspan=2, sticky='e', pady=(12, 0))
        self.botao_salvar = ttk.Button(botoes, text='Testar e salvar', command=self.testar)
        self.botao_salvar.grid(row=0, column=0, padx=(0, 6))
        ttk.Button(botoes, text='Cancelar', command=self.destroy).grid(row=0, column=1)

        self.bind('<Return>', lambda _: self.testar())
        self.campos['host'].focus_set()
        self.grab_set()

    def testar(self):
        dados = {k: c.get() for k, c in self.campos.items()}
        self.botao_salvar.state(['disabled'])
        self.status.config(text='Testando a conexão...')

        def ao_terminar(_, erro):
            self.botao_salvar.state(['!disabled'])
            if erro:
                self.status.config(text='')
                mostrar_erro(self, erro)
                return
            rd.salvar_banco(self.arquivo, **dados)
            self.salvou = True
            messagebox.showinfo(TITULO, 'Conexão OK. Configuração salva.', parent=self)
            self.destroy()

        em_segundo_plano(self, lambda: rd.testar_conexao(**dados), ao_terminar)


class Aplicativo(tk.Tk):
    def __init__(self, arquivo_config):
        super().__init__()
        self.arquivo = arquivo_config
        self.pasta_resultado = None
        self.title(TITULO)
        self.resizable(False, False)

        quadro = ttk.Frame(self, padding=20)
        quadro.grid()

        ttk.Label(quadro, text='Relatório de Receitas', font=('', 13, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(quadro, text='Escriba Document — Títulos e Documentos, PJ e Certidões', foreground='#555').grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 14))

        ini, fim = rd.mes_anterior()
        self.data_ini = self._campo_data(quadro, 2, 'Data inicial:', ini)
        self.data_fim = self._campo_data(quadro, 3, 'Data final:', fim)

        self.botao_gerar = ttk.Button(quadro, text='Gerar relatório', command=self.gerar)
        self.botao_gerar.grid(row=4, column=0, columnspan=2, sticky='we', pady=(14, 0), ipady=4)

        self.status = ttk.Label(quadro, text='', wraplength=340, justify='left')
        self.status.grid(row=5, column=0, columnspan=2, sticky='w', pady=(12, 0))

        rodape = ttk.Frame(quadro)
        rodape.grid(row=6, column=0, columnspan=2, sticky='we', pady=(12, 0))
        self.botao_pasta = ttk.Button(rodape, text='Abrir pasta do relatório', command=self.abrir_pasta)
        ttk.Button(rodape, text='Configurar banco...', command=self.configurar).pack(side='right')

        self.bind('<Return>', lambda _: self.gerar())
        if not self.arquivo.exists():
            self.after(200, self.configurar)

    def _campo_data(self, quadro, linha, rotulo, valor):
        ttk.Label(quadro, text=rotulo).grid(row=linha, column=0, sticky='w', pady=3)
        campo = ttk.Entry(quadro, width=14, justify='center')
        campo.insert(0, f'{valor:%d/%m/%Y}')
        campo.grid(row=linha, column=1, sticky='w', pady=3, padx=(8, 0))
        return campo

    def configurar(self):
        tela = TelaBanco(self, self.arquivo)
        self.wait_window(tela)
        return tela.salvou

    def gerar(self):
        if str(self.botao_gerar['state']) == 'disabled':
            return
        try:
            config = rd.carregar_config(self.arquivo)
        except rd.ConfigAusente:
            if not self.configurar():
                return
            return self.gerar()
        except rd.ErroRelatorio as e:
            return mostrar_erro(self, e)

        try:
            data_ini = rd.ler_data(self.data_ini.get())
            data_fim = rd.ler_data(self.data_fim.get())
        except rd.ErroRelatorio as e:
            return mostrar_erro(self, e)

        self.botao_gerar.state(['disabled'])
        self.botao_pasta.pack_forget()
        self.status.config(text='Gerando o relatório, aguarde...', foreground='')

        def ao_terminar(resultado, erro):
            self.botao_gerar.state(['!disabled'])
            if erro:
                self.status.config(text='O relatório não foi gerado.', foreground='#b00020')
                return mostrar_erro(self, erro)
            self.pasta_resultado = resultado.arquivo.parent
            self.status.config(text='✔ ' + rd.formatar_resumo(resultado), foreground='#1b5e20')
            self.botao_pasta.pack(side='left')

        em_segundo_plano(self, lambda: rd.gerar(config, data_ini, data_fim), ao_terminar)

    def abrir_pasta(self):
        if self.pasta_resultado:
            abrir_pasta(self.pasta_resultado)


def main():
    arquivo = rd.pasta_do_programa() / rd.CONFIG_NOME
    rd.configurar_log(arquivo.parent)
    Aplicativo(arquivo).mainloop()


if __name__ == '__main__':
    main()
