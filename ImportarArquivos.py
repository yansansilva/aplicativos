import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

@st.cache
def carregar_dados(up, modo):
	if modo == 'integralizar':
		dados_df = pd.DataFrame()
		for data_file in up:
			if data_file.type != "text/csv":
				df = pd.read_excel(data_file)
			else:
				df = pd.read_csv(data_file, sep=';', decimal=',')

			df['DATE'] = df['DATE'].astype('string')
			df['TIME'] = df['TIME'].astype('string')
			juntar = df['DATE'] + ' ' + df['TIME']
			df.insert(0, 'TEMPO', pd.to_datetime(juntar, dayfirst=True), True)

			dados_df = dados_df.append(df.drop(['DATE','TIME'], axis=1))

	elif modo == 'FDI' or modo == 'Energia':
		if up.type != "text/csv":
			dados_df = pd.read_excel(up, sheet_name=0, index_col=0)
		else:
			dados_df = pd.read_csv(up)

	return dados_df

@st.experimental_memo
def import_from_GoogleDrive():
	# Selecionar planilha
    inversores = gspread.authorize(Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive",],)).open('Dados_Simulacao').worksheet('Inversores')
    modulos = gspread.authorize(Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive",],)).open('Dados_Simulacao').worksheet('Modulos')
    ambiente = gspread.authorize(Credentials.from_service_account_info(st.secrets["gcp_service_account"],scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive",],)).open('Dados_Simulacao').worksheet('Ambiente')

    dados_inversor = pd.DataFrame(inversores.get_all_records()).set_index('Inversor')
    dados_modulo = pd.DataFrame(modulos.get_all_records()).set_index('Módulo')
    dados_ambiente = pd.DataFrame(ambiente.get_all_records())

    return dados_modulo, dados_inversor, dados_ambiente
