import pandas as pd
import streamlit as st

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class   ServicesDataProcessor:
    def __init__(self,path_csv = "data/gold/cafe.csv",coluna='À vista R$'):
        self.path_csv = path_csv
        self.coluna = coluna    
        self.df_original = pd.read_csv(self.path_csv)
# Função de agrupamento por periodicidade


    def load_data(self):
        return self.df_original.copy()
    

    def agrupar_periodicidade(self,df, periodicidade='D'):
        if df is None:
            df = self.load_data()
        df['Data'] = pd.to_datetime(df['Data'])
        df = df.set_index('Data')
        df_agrupado = df.resample(periodicidade).mean().dropna().reset_index()
        return df_agrupado

    # Extrair periodicidade da pergunta
    def extrair_periodicidade(self,pergunta):
        p = pergunta.lower()
        if 'dia' in p or 'diária' in p:
            return 'D'
        elif 'semana' in p or 'semanal' in p:
            return 'W'
        elif 'mês' in p or 'mensal' in p:
            return 'M'
        elif 'ano' in p or 'anual' in p:
            return 'A'
        return None
    