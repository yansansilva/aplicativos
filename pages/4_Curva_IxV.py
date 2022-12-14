import streamlit as st
import pandas as pd
import numpy as np
from scipy import optimize
import plotly.graph_objects as go
from ImportarArquivos import import_from_GoogleDrive

st.set_page_config(
    page_title="GEDAE Aplicativos - Curva IxV",
    page_icon="馃憢",
    layout="wide"
)

st.title("Curva IxV")

importar_dados = st.radio('Par芒metros do M贸dulo Fotovoltaico',
                          ('Digitar',
                           'Importar pr贸pria base de dados',
                           'Importar base de dados do servidor'),
                          horizontal=True)
st.write(f'''
    _________________________________________________________________________
        ''')
Pmp, Imp, Vmp, Isc, Voc, CIsc, CVoc = [0, 0, 0, 0, 0, 0, 0]

modulo = ''
if importar_dados != 'Digitar':
    st.write('### Importe os dados dos m贸dulos fotovoltaicos')
    if importar_dados == 'Importar pr贸pria base de dados':
        arquivo_modulos = st.file_uploader('Dados dos m贸dulos', type=['XLS', 'XLSX'])
        if arquivo_modulos is not None:
            dados_modulo = pd.read_excel(arquivo_modulos, sheet_name=0,
                                     index_col=0)  # Caracter铆sticas do m贸dulo fotovoltaico
            st.write('### Selecione o m贸dulo fotovoltaico')
            modulo = st.selectbox('M贸dulo', dados_modulo.columns)
    elif importar_dados == 'Importar base de dados do servidor':
        dados_modulo, dados_inversor, dados_ambiente = import_from_GoogleDrive()
        st.write('### Selecione o m贸dulo fotovoltaico')
        modulo = st.selectbox('M贸dulo', dados_modulo.columns)
    if modulo != '':
        if st.checkbox('Mostrar Dados do M贸dulo'):
            st.dataframe(dados_modulo[modulo])

        ## Caracter铆sticas el茅tricas
        Pmp = dados_modulo[modulo]['Pmp']  # Pot锚ncia el茅trica m谩xima
        Imp = dados_modulo[modulo]['Imp']  # Corrente na m谩xima pot锚ncia
        Vmp = dados_modulo[modulo]['Vmp']  # tens茫o na m谩xima pot锚ncia
        Isc = dados_modulo[modulo]['Isc']  # Corrente de curto - circuito
        Voc = dados_modulo[modulo]['Voc']  # Tens茫o de circuito aberto

        ## par芒metros t茅rmicos
        CIsc = dados_modulo[modulo][
                   'Coef. Temp. I (%)'] / 100  # Coeficiente de temperatura de Isc(N茫o est谩 expresso em porcentagem)
        CVoc = dados_modulo[modulo][
                   'Coef. Temp. V (%)'] / 100  # Coeficiente de temperatura de Voc(N茫o est谩 expresso em porcentagem)
else:
    st.write('### Digite os dados dos m贸dulos fotovoltaicos')

    modulo = st.text_input('Modelo do m贸dulo', value='')

    coluna1, coluna2, coluna3 = st.columns((2, 2, 1))

    coluna1.write('## Par芒metros el茅tricos')
    Pmp = coluna1.number_input('Pmp: ', min_value=0)  # Pot锚ncia el茅trica m谩xima
    Imp = coluna1.number_input('Imp: ', min_value=0.0)  # Corrente na m谩xima pot锚ncia
    Vmp = coluna1.number_input('Vmp: ', min_value=0.0)  # tens茫o na m谩xima pot锚ncia
    Isc = coluna1.number_input('Isc: ', min_value=0.0)  # Corrente de curto - circuito
    Voc = coluna1.number_input('Voc: ', min_value=0.0)  # Tens茫o de circuito aberto

    coluna2.write('## Par芒metros t茅rmicos')
    CIsc = coluna2.number_input('CIsc: ', min_value=0.0, step=0.001, format="%.3f")/100    # Coeficiente de temperatura de Isc(N茫o est谩 expresso em porcentagem)
    CVoc = coluna2.number_input('CVoc: ', max_value=0.0, step=0.001, format="%.3f")/100    # Coeficiente de temperatura de Voc(N茫o est谩 expresso em porcentagem)


if Pmp != 0 and Imp != 0 and Vmp != 0 and Isc != 0 and Voc != 0 and CIsc != 0 and CVoc != 0:
    # --------------------------------------------------------------------------------------
    # Par芒metros nas condi莽玫es STC
    Irradiancia_referencia = 1000
    Tac = 25
    # --------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------

    st.write('### Par芒metros ajust谩veis para Curva I-V')

    coluna1, coluna2, coluna3 = st.columns((1, 1, 2))
    coluna1.markdown('''___''')
    coluna2.markdown('''___''')

    Irradiancia = coluna1.number_input('Irradi芒ncia: ', value=1000)
    Temperatura_costa_modulo = coluna2.number_input('Temperatura de costa do modulo: ', value=25.0)
    Resistencia_serie = coluna1.number_input('Resist锚ncia serie: ', min_value=0.0, step=0.001, format="%.3f")
    Resistencia_paralelo = coluna2.number_input('Resist锚ncia paralelo: ', min_value=1, value=1000000)
    Numero_celulas_serie = coluna1.number_input('N煤mero de c茅lulas em s茅rie: ', min_value=1, value=60)
    Fator_de_idealidade = coluna2.slider('Fator de idealidade: ', min_value=1.0, max_value=2.0)

    S = Irradiancia / Irradiancia_referencia
    Tc = Temperatura_costa_modulo
    Rs = Resistencia_serie
    Rp = Resistencia_paralelo
    # --------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------
    # Dados de Cat谩logo
    Ns = Numero_celulas_serie
    Voc_Tjref = Voc / Ns
    Isc_Tjref = Isc
    ALFA = CIsc
    BETA = CVoc
    # --------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------
    # Constantes
    q = 1.6E-19
    k = 1.38E-23
    n = Fator_de_idealidade
    Eg = 1.12
    Tjref = 273 + Tac
    # --------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------
    # Atribuindo os valores para Tens茫o de M贸dulo, Tens茫o de C茅lula e de Corrente
    Va = np.linspace(0, Voc, 255)
    Vc = np.linspace(0, Voc, 255) / Ns
    # --------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------
    # C谩lculos
    Tak = Tjref
    Tj = 273 + Tc

    Voc_Tj = Voc_Tjref * (1 + BETA * (Tj - Tjref))
    Isc_Tj = Isc_Tjref * (1 + ALFA * (Tj - Tjref))

    Vt_Ta = n * k * Tjref / q

    Iph_Tjref = Isc_Tj * S
    Iph = Iph_Tjref + ALFA * (Tj - Tjref)
    Io_Tjref = Isc_Tj / (np.exp(Voc_Tj / Vt_Ta) - 1)
    Io = Io_Tjref * (Tak / Tjref) ** (3 / n) * np.exp(-q * Eg / (n * k) * ((1 / Tak) - (1 / Tjref)))

    # --------------------------------------------------------------------------------------
    # M茅todo de Newton
    f = lambda I, Vc: Iph - I - Io * (np.exp((Vc + I * Rs) / Vt_Ta) - 1) - (Vc + I * Rs) / Rp
    fder = lambda I, Vc: - 1 - (Io * (np.exp((Vc + I * Rs) / Vt_Ta) - 1)) * Rs / Vt_Ta - Rs / Rp
    I = [0 for x in range(len(Vc))]
    I_res = optimize.newton(f, I, fprime=fder, args=(Vc,), maxiter=100)
    # --------------------------------------------------------------------------------------

    resultado = pd.DataFrame(zip(*[I_res, Va]), columns=['I_res', 'Va'])

    importar_curva_medida = st.checkbox('Plotar curva IxV medida')
    curva_medida = pd.DataFrame()
    if importar_curva_medida:
        st.write('#### Importe a curva IxV medida:')
        arquivo_curva_medida = st.file_uploader('Curva IxV medida', type=['XLS', 'XLSX'])
        if arquivo_curva_medida is not None:
            curva_medida = pd.read_excel(arquivo_curva_medida)

    fig = go.Figure()
    fig.add_trace(go.Line(x=resultado[resultado['I_res'] >= 0]['Va'],
                          y=resultado[resultado['I_res'] >= 0]['I_res']))

    if not curva_medida.empty:
        fig.add_trace(go.Line(x=curva_medida['V'],
                              y=curva_medida['I']))

    fig.update_layout(
        title=f'Curva IxV: {modulo}',
        title_x=0.5,
        title_y=0.85,
        xaxis_title='Tens茫o do m贸dulo (V)',
        yaxis_title='Corrente do m贸dulo (A)',
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
        ),
        showlegend=False,
        width=700, height=400
    )

    coluna3.plotly_chart(fig)
    # --------------------------------------------------------------------------------------
