import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title = "Dashboard de Salários na Área de Dados",
    page_icon="📊",  # icone da pagina
    layout="wide",   # largura da pagina
)

# Carregamento de dados
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Barra lateral filtros
st.sidebar.header("🔎Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())  # df foi carregado e a coluna do ano foi usada e ordena-los em valores unicos
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default = anos_disponiveis) # opçao de escolher

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default = senioridades_disponiveis)

# Filtro por Tipo de contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default = contratos_disponiveis)

# Filtro por tamanho de empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho de Empresa", tamanhos_disponiveis, default = tamanhos_disponiveis)

# Filtragem do DataFrame
# o dataframe original é filtrado com base nas seleções feitas na barra lateral
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# Conteúdo Principal
st.title("📊 Dashboard de Salários na Área de Dados")
st.markdown("Explore os dados de salários na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.") 

# Métricas principais
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0,  ""   

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"{total_registros}")
col4.metric("Cargo Mais Comum", f"{cargo_mais_frequente}")
st.markdown("---")

# Analises visuais com Plotly
st.subheader("Gráficos")    # subtitulos

col_graf1, col_graf2 = st.columns(2)   # definindo duas colunas para os graficos

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x = 'usd',
            y = 'cargo',
            orientation = 'h',  # horizontal
            title = "Top 10 cargos por saário médio",
            labels = {'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x = 0.1, yaxis = {'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)  # conseguir exibir o grafico
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")  # aviso 

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x = 'usd',
            nbins = 30,
            title = "Distribuição de salários",
            labels = {'usd': 'Faixa Salarial (USD)', 'count': ''}
        )        
        grafico_hist.update_layout(title_x = 0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição salarial.")  # aviso

col_graf3, col_graf4 = st.columns(2)

with col_graf3:      # grafico rosca
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")
        
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.") 

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)

