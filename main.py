import os
import pandas as pd


# Carregar os dados
enem_matematica_df = pd.read_csv("./tabelas/enem-matematica_-_Pagina1.csv")
quantidade_questoes_tema_df = pd.read_excel("./tabelas/quantidade_questoes_tema.xlsx")

# Limpeza do DataFrame enem_matematica_df
enem_matematica_df = enem_matematica_df.dropna(thresh=4).reset_index(drop=True)
enem_matematica_df.columns = [
    "Ano",
    "Unidade da Federação",
    "Participantes do ENEM",
    "Média",
    "Mediana",
    "Moda",
    "Mínimo",
    "Máximo",
    "Desvio Padrão",
]
enem_matematica_df = enem_matematica_df[enem_matematica_df["Ano"].notna()]
enem_matematica_df = enem_matematica_df[["Ano", "Média"]].astype({"Ano": int})
enem_matematica_df["Média"] = (
    enem_matematica_df["Média"].str.replace(",", ".").astype(float)
)

# Limpeza do DataFrame quantidade_questoes_tema_df
quantidade_questoes_tema_df.columns = quantidade_questoes_tema_df.columns.str.replace(
    " ", "_"
)
quantidade_questoes_tema_df = quantidade_questoes_tema_df.rename(
    columns=lambda x: x.replace("ENEM_-_", "").replace("_", " ").strip()
)

# Ajustes nos dados para alinhamento
corr_df = quantidade_questoes_tema_df.copy()
corr_df["Ano"] = enem_matematica_df["Ano"]
corr_df = corr_df.set_index("Ano")

# Alinhar corretamente os anos
corr_df = corr_df.loc[enem_matematica_df["Ano"]]
corr_df["Média"] = enem_matematica_df.set_index("Ano")["Média"]

if not os.path.exists("./tabelas_tratadas"):
    os.mkdir("./tabelas_tratadas")

# Exportação dos dados para CSV
enem_matematica_df.to_csv("./tabelas_tratadas/enem_matematica_limpo.csv", index=False)
quantidade_questoes_tema_df.to_csv(
    "./tabelas_tratadas/quantidade_questoes_tema_limpo.csv", index=False
)

# Transformar os dados de disciplinas para formato longo (long format)
disciplinas_long_df = quantidade_questoes_tema_df.melt(
    id_vars=["Categoria"], var_name="Ano", value_name="Quantidade"
)

# Converter as colunas 'Ano' para string para garantir a compatibilidade
enem_matematica_df["Ano"] = enem_matematica_df["Ano"].astype(str)
disciplinas_long_df["Ano"] = disciplinas_long_df["Ano"].astype(str)

# Calcular a porcentagem de cada tema em relação ao total de 45 questões
disciplinas_long_df["Porcentagem"] = (disciplinas_long_df["Quantidade"] / 45) * 100

# Encontrar a disciplina que mais caiu em cada ano
max_disciplinas_df = disciplinas_long_df.loc[
    disciplinas_long_df.groupby("Ano")["Quantidade"].idxmax()
]

# Tabela 1: Ano, Média, Disciplina, Porcentagem
tabela_1 = pd.merge(enem_matematica_df, disciplinas_long_df, on="Ano")
tabela_1 = tabela_1[["Ano", "Média", "Categoria", "Porcentagem"]]

# Salvar as tabelas em arquivos CSV
tabela_1.to_csv("./tabelas_tratadas/dados_normalizados.csv", index=False)
