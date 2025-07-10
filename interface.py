import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import os
from pdf_processor import PDFProcessor
import sys


def get_resource_path(relative_path):
    """Retorna o caminho absoluto, considerando o PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class PDFExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extrator de Chaves de Acesso PDF v2.0")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
                
        self.processor = PDFProcessor()
        self.processando = False
        self.pasta_selecionada = None
        
        self.criar_interface()
        
        # Define pasta atual como padrão
        self.processor.definir_pasta_trabalho()
        self.atualizar_pasta_display()
    
    def criar_interface(self):
        # ícone da janela
        self.root.iconbitmap(get_resource_path("monster.ico"))
        
        # Título
        titulo = tk.Label(
            self.root, 
            text="Extrator de Chaves de Acesso PDF v2.0",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        titulo.pack(pady=10)
        
        # Subtítulo
        subtitulo = tk.Label(
            self.root, 
            text="Versão melhorada - Extração mais precisa",
            font=("Arial", 10, "italic"),
            fg="#7f8c8d"
        )
        subtitulo.pack(pady=5)
        
        # Frame de seleção de pasta
        frame_pasta = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=2)
        frame_pasta.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_pasta, text="PASTA DE TRABALHO:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        pasta_frame = tk.Frame(frame_pasta)
        pasta_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.label_pasta = tk.Label(
            pasta_frame,
            text="Pasta atual: " + os.getcwd(),
            font=("Arial", 9),
            fg="#34495e",
            wraplength=500,
            justify=tk.LEFT
        )
        self.label_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_selecionar_pasta = tk.Button(
            pasta_frame,
            text="Selecionar Pasta",
            command=self.selecionar_pasta,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_selecionar_pasta.pack(side=tk.RIGHT, padx=5)
        
        # Frame de instruções
        frame_instrucoes = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=2)
        frame_instrucoes.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_instrucoes, text="INSTRUÇÕES:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        
        instrucoes = [
            "1. Selecione a pasta com os PDFs (ou use a pasta atual)",
            "2. Clique em 'Iniciar Processamento'",
            "3. O programa extrairá as chaves automaticamente",
            "4. As chaves serão salvas em 'chaves_acesso.txt'"
        ]
        
        for instrucao in instrucoes:
            tk.Label(frame_instrucoes, text=instrucao, font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=2)
        
        # Frame de status
        frame_status = tk.Frame(self.root)
        frame_status.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_status, text="Status:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.label_status = tk.Label(
            frame_status, 
            text="Pronto para iniciar",
            font=("Arial", 10),
            fg="#27ae60"
        )
        self.label_status.pack(anchor=tk.W, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            frame_status, 
            length=500, 
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        # Botões
        frame_botoes = tk.Frame(self.root)
        frame_botoes.pack(pady=20)
        
        self.btn_iniciar = tk.Button(
            frame_botoes,
            text="Iniciar Processamento",
            command=self.iniciar_processamento,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            border=4
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)
        
        self.btn_abrir_arquivo = tk.Button(
            frame_botoes,
            text="Abrir Arquivo de Saída",
            command=self.abrir_arquivo_saida,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2
        )
        self.btn_abrir_arquivo.pack(side=tk.LEFT, padx=10)
        
        btn_limpar_log = tk.Button(
            frame_botoes,
            text="Limpar Log",
            command=self.limpar_log,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            height=2
        )
        btn_limpar_log.pack(side=tk.LEFT, padx=10)
        
        # Área de log
        frame_log = tk.Frame(self.root)
        frame_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame_log, text="Log de Processamento:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.text_log = scrolledtext.ScrolledText(
            frame_log,
            height=12,
            width=80,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.text_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame de estatísticas
        frame_stats = tk.Frame(self.root)
        frame_stats.pack(fill=tk.X, padx=20, pady=5)
        
        self.label_contador = tk.Label(
            frame_stats,
            text="Chaves encontradas: 0",
            font=("Arial", 10, "bold"),
            fg="#e74c3c"
        )
        self.label_contador.pack(side=tk.LEFT)
        
        self.label_progresso = tk.Label(
            frame_stats,
            text="Progresso: 0/0",
            font=("Arial", 10, "bold"),
            fg="#3498db"
        )
        self.label_progresso.pack(side=tk.RIGHT)
    
    def selecionar_pasta(self):
        """Abre diálogo para selecionar pasta"""
        pasta = filedialog.askdirectory(
            title="Selecione a pasta com os PDFs",
            initialdir=self.processor.pasta_trabalho or os.getcwd()
        )
        
        if pasta:
            self.processor.definir_pasta_trabalho(pasta)
            self.atualizar_pasta_display()
            self.adicionar_log(f"Pasta selecionada: {pasta}")
    
    def atualizar_pasta_display(self):
        """Atualiza o display da pasta selecionada"""
        if self.processor.pasta_trabalho:
            self.label_pasta.config(text=f"Pasta atual: {self.processor.pasta_trabalho}")
    
    def adicionar_log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.text_log.config(state=tk.NORMAL)
        self.text_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {mensagem}\n")
        self.text_log.config(state=tk.DISABLED)
        self.text_log.see(tk.END)
        self.root.update()
    
    def limpar_log(self):
        """Limpa o log de processamento"""
        self.text_log.config(state=tk.NORMAL)
        self.text_log.delete(1.0, tk.END)
        self.text_log.config(state=tk.DISABLED)
    
    def atualizar_status(self, status, cor="#2c3e50"):
        """Atualiza o status na interface"""
        self.label_status.config(text=status, fg=cor)
        self.root.update()
    
    def atualizar_progresso(self, atual, total):
        """Atualiza a barra de progresso"""
        if total > 0:
            self.progress['value'] = (atual / total) * 100
            self.label_progresso.config(text=f"Progresso: {atual}/{total}")
        else:
            self.progress['value'] = 0
            self.label_progresso.config(text="Progresso: 0/0")
        self.root.update()
    
    def iniciar_processamento(self):
        """Inicia o processamento em thread separada"""
        if self.processando:
            messagebox.showwarning("Aviso", "Processamento já em andamento!")
            return
        
        # Verifica se há PDFs na pasta
        pdfs = self.processor.encontrar_pdfs_na_pasta()
        if not pdfs:
            messagebox.showwarning(
                "Aviso", 
                f"Nenhum PDF encontrado na pasta:\n{self.processor.pasta_trabalho}"
            )
            return
        
        resposta = messagebox.askyesno(
            "Confirmação",
            f"Encontrados {len(pdfs)} PDFs na pasta.\n\nDeseja iniciar o processamento?"
        )
        
        if resposta:
            self.processando = True
            self.btn_iniciar.config(state=tk.DISABLED)
            
            # Inicia thread de processamento
            thread = threading.Thread(target=self.processar_pdfs_thread)
            thread.daemon = True
            thread.start()
    
    def processar_pdfs_thread(self):
        """Thread de processamento dos PDFs"""
        try:
            self.atualizar_status("Iniciando processamento...", "#f39c12")
            self.adicionar_log("=== INICIANDO PROCESSAMENTO ===")
            
            # Gerencia arquivo de saída
            self.processor.gerenciar_arquivo_saida()
            
            # Encontra PDFs
            pdfs = self.processor.encontrar_pdfs_na_pasta()
            
            if not pdfs:
                self.adicionar_log("❌ Nenhum PDF encontrado na pasta atual")
                self.atualizar_status("Nenhum PDF encontrado", "#e74c3c")
                return
            
            self.adicionar_log(f"✓ Encontrados {len(pdfs)} PDFs")
            self.atualizar_progresso(0, len(pdfs))
            
            # Processa cada PDF
            for i, pdf in enumerate(pdfs, 1):
                self.atualizar_status(f"Processando PDF {i}/{len(pdfs)}", "#3498db")
                self.adicionar_log(f"📄 [{i}/{len(pdfs)}] Processando: {pdf['nome']}")
                
                try:
                    sucesso = self.processor.processar_pdf(pdf)
                    
                    # Atualiza contador
                    total_chaves = len(self.processor.chaves_encontradas)
                    self.label_contador.config(text=f"Chaves encontradas: {total_chaves}")
                    
                    if sucesso:
                        self.adicionar_log(f"✓ Chave extraída com sucesso")
                    else:
                        self.adicionar_log(f"❌ Chave não encontrada")
                        
                except Exception as e:
                    self.adicionar_log(f"❌ Erro ao processar {pdf['nome']}: {str(e)}")
                    
                finally:
                    self.atualizar_progresso(i, len(pdfs))
            
            # Salva arquivo
            self.processor.salvar_chaves_arquivo()
            self.adicionar_log("💾 Chaves salvas em 'chaves_acesso.txt'")
            
            # Finaliza
            total_chaves = len(self.processor.chaves_encontradas)
            self.atualizar_status(f"Concluído! {total_chaves} chaves encontradas", "#27ae60")
            self.adicionar_log(f"🎉 Processamento concluído! Total: {total_chaves} chaves")
            
            messagebox.showinfo("Sucesso", f"Processamento concluído!\nTotal de chaves encontradas: {total_chaves}")
            
        except Exception as e:
            self.adicionar_log(f"❌ Erro geral: {str(e)}")
            self.atualizar_status("Erro durante processamento", "#e74c3c")
            messagebox.showerror("Erro", f"Erro durante o processamento:\n{str(e)}")
        
        finally:
            self.processando = False
            self.btn_iniciar.config(state=tk.NORMAL)
            self.progress['value'] = 0
    
    def abrir_arquivo_saida(self):
        arquivo_saida = os.path.join(self.processor.pasta_trabalho, self.processor.arquivo_saida)
        """Abre o arquivo de saída"""
        if os.path.exists(arquivo_saida):
            try:
                os.startfile(arquivo_saida)  # Windows
            except:
                try:
                    os.system(f'xdg-open {arquivo_saida}')  # Linux
                except:
                    try:
                        os.system(f'open {arquivo_saida}')  # macOS
                    except:
                        messagebox.showinfo("Arquivo", f"Arquivo salvo em: {arquivo_saida}")
        else:
            messagebox.showwarning("Aviso", "Arquivo de saída não encontrado. Execute o processamento primeiro.")

def main():
    root = tk.Tk()
    app = PDFExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()