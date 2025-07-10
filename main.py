#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extrator de Chaves de Acesso PDF
Versão 2.0 - Melhorada e Otimizada

Autor: Assistant
Data: 2025

Dependências:
- pyautogui
- pytesseract 
- opencv-python
- pillow
- pyperclip
- tkinter (já vem com Python)

Instalação:
pip install pyautogui pytesseract opencv-python pillow pyperclip

Uso:
python main.py
"""

import sys
import os

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = [
        'pyperclip',
        'tkinter'
    ]
    
    faltando = []
    
    for dep in dependencias:
        try:
            if dep == 'cv2':
                import cv2
            elif dep == 'PIL':
                from PIL import Image
            elif dep == 'tkinter':
                import tkinter
            else:
                __import__(dep)
        except ImportError:
            faltando.append(dep)
    
    if faltando:
        print("❌ Dependências faltando:")
        for dep in faltando:
            print(f"  - {dep}")
        print("\n📦 Para instalar:")
        print("pip install pyautogui pytesseract opencv-python pillow pyperclip")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def verificar_tesseract():
    """Verifica se o Tesseract OCR está instalado"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR encontrado!")
        return True
    except:
        print("❌ Tesseract OCR não encontrado!")
        print("\n📥 Para instalar:")
        print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("macOS: brew install tesseract")
        return False

def main():
    """Função principal"""
    print("🔍 Extrator de Chaves de Acesso PDF")
    print("=" * 40)
    
    # Verifica dependências
    if not verificar_dependencias():
        input("\nPressione Enter para sair...")
        sys.exit(1)
    
    # Verifica Tesseract
    # if not verificar_tesseract():
    #     input("\nPressione Enter para sair...")
    #     sys.exit(1)
    
    print("\n🚀 Iniciando interface gráfica...")
    
    try:
        # Importa e executa a interface
        from interface import main as run_gui
        run_gui()
        
    except ImportError as e:
        print(f"❌ Erro ao importar interface: {e}")
        print("Certifique-se de que todos os arquivos estão na mesma pasta:")
        print("  - main.py")
        print("  - interface.py") 
        print("  - pdf_processor.py")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    finally:
        print("\n👋 Programa encerrado.")

if __name__ == "__main__":
    main()