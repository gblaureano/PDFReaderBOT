import os
import re
import time
import glob
from datetime import datetime

import pyperclip
import pypdf as PyPDF2

class PDFProcessor:
    def __init__(self):
        self.chaves_encontradas = []
        self.arquivo_saida = "chaves_acesso.txt"
        self.pasta_trabalho = None
    
        
        # Padrões para buscar chaves de acesso
        self.padroes_chave = [
            r'CHAVE\s+DE\s+ACESSO[:\s]*(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
            r'CHAVE\s+DE\s+ACESSO[:\s]*(\d{44,44})',
            r'CHAVE[:\s]*(\d{44,44})',
            r'ACESSO[:\s]*(\d{44,44})',
            r'(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
            r'(\d{44,44})'
        ]
    
    def definir_pasta_trabalho(self, pasta=None):
        """Define a pasta de trabalho para buscar PDFs"""
        if pasta is None:
            # Usa a pasta atual
            self.pasta_trabalho = os.getcwd()
        else:
            if os.path.exists(pasta):
                self.pasta_trabalho = pasta
            else:
                raise FileNotFoundError(f"Pasta não encontrada: {pasta}")
        
        print(f"Pasta de trabalho definida: {self.pasta_trabalho}")
    
    def get_caminho_saida(self):
        """Retorna o caminho completo para o arquivo de saída"""
        return os.path.join(self.pasta_trabalho, self.arquivo_saida)
    
    def encontrar_pdfs_na_pasta(self, pasta=None):
        """Encontra todos os PDFs na pasta especificada"""
        if pasta:
            self.definir_pasta_trabalho(pasta)
        elif not self.pasta_trabalho:
            self.definir_pasta_trabalho()
        
        # Busca por arquivos PDF
        padrao_pdf = os.path.join(self.pasta_trabalho, "*.pdf")
        arquivos_pdf = glob.glob(padrao_pdf)
        
        pdfs_encontrados = []
        for arquivo in arquivos_pdf:
            nome_arquivo = os.path.basename(arquivo)
            pdfs_encontrados.append({
                'nome': nome_arquivo,
                'caminho': arquivo
            })
        
        print(f"Encontrados {len(pdfs_encontrados)} PDFs na pasta")
        return pdfs_encontrados
    
    def extrair_texto_pdf(self, caminho_pdf):
        """Extrai texto de um PDF usando PyPDF2"""
        texto_completo = ""
        
        try:
            with open(caminho_pdf, 'rb') as arquivo:
                reader = PyPDF2.PdfReader(arquivo)
                
                # Extrai texto de todas as páginas
                for pagina_num in range(len(reader.pages)):
                    pagina = reader.pages[pagina_num]
                    texto_pagina = pagina.extract_text()
                    texto_completo += texto_pagina + "\n"
                
                print(f"✓ Texto extraído de {len(reader.pages)} páginas")
                return texto_completo
                
        except Exception as e:
            print(f"❌ Erro ao extrair texto do PDF: {e}")
            return ""
    
    def encontrar_chave_no_texto(self, texto, nome_arquivo):
        """Encontra a chave de acesso no texto extraído"""
        # Normaliza o texto (remove quebras de linha desnecessárias)
        texto_normalizado = re.sub(r'\s+', ' ', texto.upper())
        
        # Tenta cada padrão de chave
        for padrao in self.padroes_chave:
            matches = re.finditer(padrao, texto_normalizado, re.IGNORECASE)
            
            for match in matches:
                chave_bruta = match.group(1) if match.groups() else match.group(0)
                
                # Limpa a chave (remove espaços, hífens, etc.)
                chave_limpa = re.sub(r'[^0-9]', '', chave_bruta)
                
                # Valida o tamanho da chave
                if len(chave_limpa) >= 32:  # Chave de acesso típica tem 32+ dígitos
                    print(f"✓ Chave encontrada: {chave_limpa}")
                    return chave_limpa
        
        # Se não encontrou com padrões específicos, busca sequências longas de números
        numeros_longos = re.findall(r'\d{32,}', texto_normalizado)
        if numeros_longos:
            chave = numeros_longos[0]
            print(f"✓ Chave encontrada (sequência numérica): {chave}")
            return chave
        
        print(f"❌ Nenhuma chave encontrada em {nome_arquivo}")
        return None
    
    def processar_pdf(self, pdf_info):
        """Processa um único PDF"""
        print(f"\n--- Processando: {pdf_info['nome']} ---")
        
        # Extrai texto do PDF
        texto_pdf = self.extrair_texto_pdf(pdf_info['caminho'])
        
        if not texto_pdf:
            print("❌ Não foi possível extrair texto do PDF")
            return False
        
        # Procura pela chave de acesso no texto
        chave = self.encontrar_chave_no_texto(texto_pdf, pdf_info['nome'])
        
        if chave:
            self.chaves_encontradas.append({
                'arquivo': pdf_info['nome'],
                'chave': chave,
                'caminho': pdf_info['caminho']
            })
            
            # Copia a chave para a área de transferência
            try:
                pyperclip.copy(chave)
                print(f"✓ Chave copiada para área de transferência")
            except:
                print("⚠️ Não foi possível copiar para área de transferência")
            
            return True
        else:
            return False
    
    def gerenciar_arquivo_saida(self):
        """Gerencia o arquivo de saída (limpa se existir, cria se não)"""
        caminho_saida = self.get_caminho_saida()
        
        if os.path.exists(caminho_saida):
            print(f"Arquivo {caminho_saida} já existe. Limpando conteúdo...")
            with open(caminho_saida, 'w', encoding='utf-8') as arquivo:
                arquivo.write("")
        else:
            print(f"Criando arquivo {caminho_saida}...")
    
    def salvar_chaves_arquivo(self):
        """Salva todas as chaves encontradas no arquivo"""
        caminho_saida = self.get_caminho_saida()
        
        with open(caminho_saida, 'w', encoding='utf-8') as arquivo:
            arquivo.write("CHAVES DE ACESSO EXTRAÍDAS\n")
            arquivo.write("=" * 50 + "\n")
            arquivo.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            arquivo.write(f"Pasta: {self.pasta_trabalho}\n")
            arquivo.write(f"Total de arquivos processados: {len(self.chaves_encontradas)}\n\n")
            
            for i, item in enumerate(self.chaves_encontradas, 1):
                arquivo.write(f"{i:2d}. Arquivo: {item['arquivo']}\n")
                arquivo.write(f"    Chave: {item['chave']}\n")
                arquivo.write(f"    Caminho: {item['caminho']}\n")
                arquivo.write("-" * 50 + "\n")
        
        print(f"\n💾 Chaves salvas em: {caminho_saida}")
        print(f"📊 Total de chaves encontradas: {len(self.chaves_encontradas)}")
    
    def processar_todos_pdfs(self, pasta=None):
        """Função principal que processa todos os PDFs"""
        print("=== INICIANDO PROCESSAMENTO ===")
        
        # Gerencia arquivo de saída
        self.gerenciar_arquivo_saida()
        
        # Encontra todos os PDFs na pasta
        pdfs = self.encontrar_pdfs_na_pasta(pasta)
        
        if not pdfs:
            print("❌ Nenhum PDF encontrado na pasta atual")
            return False
        
        print(f"\n📄 Processando {len(pdfs)} arquivos PDF...")
        
        # Processa cada PDF
        sucessos = 0
        for i, pdf in enumerate(pdfs, 1):
            print(f"\n[{i}/{len(pdfs)}] Processando PDF...")
            try:
                if self.processar_pdf(pdf):
                    sucessos += 1
            except Exception as e:
                print(f"❌ Erro ao processar {pdf['nome']}: {e}")
                continue
        
        # Salva todas as chaves encontradas
        self.salvar_chaves_arquivo()
        
        print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"📊 Sucessos: {sucessos}/{len(pdfs)}")
        
        return True
    
    def buscar_pasta_interativa(self):
        """Permite ao usuário selecionar uma pasta"""
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()  # Oculta a janela principal
        
        pasta_selecionada = filedialog.askdirectory(
            title="Selecione a pasta com os PDFs",
            initialdir=os.getcwd()
        )
        
        root.destroy()
        
        if pasta_selecionada:
            self.definir_pasta_trabalho(pasta_selecionada)
            return pasta_selecionada
        else:
            return None
    
    def obter_estatisticas(self):
        """Retorna estatísticas do processamento"""
        return {
            'total_processados': len(self.chaves_encontradas),
            'pasta_trabalho': self.pasta_trabalho,
            'arquivo_saida': self.get_caminho_saida()
        }