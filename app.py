import streamlit as st
import pandas as pd
from engine import create_companies, set_decisions, simulate_period, compute_ranking

st.set_page_config(page_title="Simulador de Empresas", layout="wide")

if "companies" not in st.session_state:
    st.session_state.companies = None
if "period" not in st.session_state:
    st.session_state.period = 1

st.title("Simulador de Empresas — Versión Web")

col1, col2 = st.columns(2)
with col1:
    n_empresas = st.number_input("Número de empresas", min_value=1, max_value=20, value=3, step=1)
with col2:
    if st.button("Inicializar simulación"):
        st.session_state.companies = create_companies(n_empresas)
        st.session_state.period = 1
        st.success("Simulación inicializada.")

if st.session_state.companies is None:
    st.info("Inicializa la simulación para empezar.")
    st.stop()

st.subheader(f"Periodo {st.session_state.period} — Decisiones")

tabs = st.tabs([c.state.name for c in st.session_state.companies] + ["Informe"])

# Pestañas de decisiones por empresa
for tab, company in zip(tabs[:-1], st.session_state.companies):
    with tab:
        st.markdown(f"### {company.state.name}")
        price = st.number_input(f"Precio ({company.state.name})", min_value=1.0, max_value=1000.0, value=50.0, step=1.0)
        budget = st.number_input(f"Presupuesto marketing ({company.state.name})", min_value=0.0, max_value=1_000_000.0, value=10000.0, step=1000.0)
        quality = st.slider(f"Calidad ({company.state.name})", min_value=1, max_value=10, value=7)
        production = st.number_input(f"Producción planificada ({company.state.name})", min_value=0.0, max_value=1_000_000.0, value=3000.0, step=100.0)
        mot_actions = st.slider(f"Acciones motivación ({company.state.name})", min_value=0, max_value=3, value=1)

        set_decisions(company, price, budget, quality, production, mot_actions)

# Botón de simulación
if st.button("Simular periodo"):
    simulate_period(st.session_state.companies)
    ranking = compute_ranking(st.session_state.companies)

    st.subheader("Resultados del periodo")
    data = []
    for c in st.session_state.companies:
        data.append({
            "Empresa": c.state.name,
            "Ventas": round(c.sales_units, 0),
            "Ingresos": round(c.revenue, 2),
            "Resultado neto": round(c.net_result, 2),
            "Motivación": round(c.state.motivation, 2),
            "Liquidez": round(c.kpis["liquidity"], 2),
            "Solvencia": round(c.kpis["solvency"], 2),
            "Margen neto": round(c.kpis["margin_net"], 3),
        })
    df_res = pd.DataFrame(data)
    st.dataframe(df_res, use_container_width=True)

    st.subheader("Ranking")
    rank_rows = []
    for pos, (name, score, net) in enumerate(ranking, start=1):
        rank_rows.append({
            "Posición": pos,
            "Empresa": name,
            "Score": round(score, 3),
            "Resultado neto": round(net, 2),
        })
    df_rank = pd.DataFrame(rank_rows)
    st.dataframe(df_rank, use_container_width=True)

    st.session_state.period += 1

    csv_res = df_res.to_csv(index=False).encode("utf-8")
    csv_rank = df_rank.to_csv(index=False).encode("utf-8")

    st.download_button("Descargar resultados (CSV)", data=csv_res, file_name=f"resultados_periodo_{st.session_state.period-1}.csv", mime="text/csv")
    st.download_button("Descargar ranking (CSV)", data=csv_rank, file_name=f"ranking_periodo_{st.session_state.period-1}.csv", mime="text/csv")

# Pestaña de informe interno
with tabs[-1]:
    st.header("Informe Interno del Periodo")

    if "companies" not in st.session_state or st.session_state.companies is None:
        st.info("Simula al menos un periodo para ver el informe.")
    else:
        informes = []
        for c in st.session_state.companies:
            informes.append({
                "Empresa": c.state.name,
                "Caja": round(c.state.cash, 2),
                "Patrimonio Neto": round(c.state.equity, 2),
                "Deuda LP": round(c.state.long_debt, 2),
                "Deuda CP": round(c.state.short_debt, 2),
                "Ventas": round(c.sales_units, 0),
                "Ingresos": round(c.revenue, 2),
                "Resultado Operativo": round(c.op_result, 2),
                "Resultado Neto": round(c.net_result, 2),
                "Motivación": round(c.state.motivation, 2),
                "Productividad": round(1 + 0.01 * (c.state.motivation * 100), 2),
                "Liquidez": round(c.kpis["liquidity"], 2),
                "Solvencia": round(c.kpis["solvency"], 2),
                "Margen Neto": round(c.kpis["margin_net"], 3),
            })

        df_inf = pd.DataFrame(informes)
        st.dataframe(df_inf, use_container_width=True)

        csv_inf = df_inf.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar informe (CSV)",
            data=csv_inf,
            file_name=f"informe_periodo_{st.session_state.period-1}.csv",
            mime="text/csv"
        )
