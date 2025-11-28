
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Agente de Optimización Hotelera - HotelDo",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar datos
@st.cache_data
def load_data():
    df_hound = pd.read_excel('detallehound_data.xlsx', sheet_name=0)
    df_requests = pd.read_csv('requests_data.csv')
    
    # Limpiar datos de requests
    def clean_numeric(val):
        if pd.isna(val) or val == 'nan':
            return 0
        if isinstance(val, str):
            return float(val.replace(',', ''))
        return float(val)
    
    df_requests['total_requests'] = df_requests['total_requests'].apply(clean_numeric)
    df_requests['total_availability'] = df_requests['total_availability'].apply(clean_numeric)
    df_requests['gb'] = df_requests['gb'].apply(clean_numeric)
    df_requests['hotelid'] = df_requests['hotelid'].apply(lambda x: str(x).replace(',', ''))
    
    return df_hound, df_requests

df_hound, df_requests = load_data()

# FUNCIONES DEL AGENTE
def get_pricing_competitiveness(hotel_name, channel='B2B'):
    hotel_data = df_hound[df_hound['Nombre_Hotel'] == hotel_name]
    
    if len(hotel_data) == 0:
        return {"error": "Hotel no encontrado"}
    
    var_col = 'Var_B2B' if channel == 'B2B' else 'Var_B2C'
    pam_col = 'PamBaseRate ($)' if channel == 'B2B' else 'PAM_B2C ($)'
    
    data_valida = hotel_data[hotel_data[var_col].notna()].copy()
    
    if len(data_valida) == 0:
        return {"error": "No hay datos disponibles"}
    
    var_promedio = data_valida[var_col].mean()
    precio_promedio = data_valida[pam_col].mean()
    casos_total = len(data_valida)
    casos_mas_caros = (data_valida[var_col] > 0).sum()
    casos_competitivos = (data_valida[var_col] <= 0).sum()
    
    return {
        "hotel": hotel_name,
        "channel": channel,
        "var_promedio": var_promedio,
        "precio_promedio_pam": precio_promedio,
        "casos_total": casos_total,
        "casos_mas_caros": casos_mas_caros,
        "casos_competitivos": casos_competitivos,
        "pct_competitivos": casos_competitivos / casos_total
    }

def get_demand_analysis(hotel_id):
    hotel_data = df_requests[df_requests['hotelid'] == str(hotel_id)].copy()
    
    if len(hotel_data) == 0:
        return {"error": "No hay datos de demanda"}
    
    total_requests = hotel_data['total_requests'].sum()
    total_availability = hotel_data['total_availability'].sum()
    lost_requests = total_requests - total_availability
    total_orders = hotel_data['orders'].sum()
    total_gb = hotel_data['gb'].sum()
    
    hotel_data['lost_requests'] = hotel_data['total_requests'] - hotel_data['total_availability']
    
    nat_stats = hotel_data.groupby('nationality').agg({
        'total_requests': 'sum',
        'total_availability': 'sum',
        'lost_requests': 'sum',
        'orders': 'sum',
        'gb': 'sum'
    }).reset_index()
    
    nat_stats = nat_stats.sort_values('lost_requests', ascending=False).head(10)
    
    return {
        "hotel_id": hotel_id,
        "total_requests": total_requests,
        "total_availability": total_availability,
        "lost_requests": lost_requests,
        "availability_rate": total_availability / total_requests if total_requests > 0 else 0,
        "lost_rate": lost_requests / total_requests if total_requests > 0 else 0,
        "total_orders": total_orders,
        "conversion_rate": total_orders / total_requests if total_requests > 0 else 0,
        "total_gb": total_gb,
        "top_lost_nationalities": nat_stats.to_dict('records')
    }

def get_recommendations(hotel_name, hotel_id):
    pricing_b2b = get_pricing_competitiveness(hotel_name, 'B2B')
    pricing_b2c = get_pricing_competitiveness(hotel_name, 'B2C')
    demand = get_demand_analysis(hotel_id)
    
    recommendations = []
    
    # Pricing B2B
    if 'error' not in pricing_b2b:
        if pricing_b2b['var_promedio'] > 0.05:
            recommendations.append({
                "tipo": "🔴 PRICING - Reducción de Tarifa",
                "prioridad": "ALTA",
                "canal": "B2B",
                "insight": f"Tu tarifa promedio está {pricing_b2b['var_promedio']:.1%} por encima del mercado",
                "accion": f"Considera reducir tarifas en un {min(pricing_b2b['var_promedio'], 0.15):.1%}",
                "impacto": "Aumentar conversión en búsquedas B2B"
            })
        elif pricing_b2b['var_promedio'] < -0.05:
            recommendations.append({
                "tipo": "🟡 PRICING - Oportunidad de Revenue",
                "prioridad": "MEDIA",
                "canal": "B2B",
                "insight": f"Tu tarifa está {abs(pricing_b2b['var_promedio']):.1%} por debajo del mercado",
                "accion": f"Puedes incrementar tarifas hasta {abs(pricing_b2b['var_promedio'])/2:.1%} sin perder competitividad",
                "impacto": "Incremento de revenue sin afectar posición"
            })
    
    # Pricing B2C
    if 'error' not in pricing_b2c:
        if pricing_b2c['var_promedio'] > 0.05:
            recommendations.append({
                "tipo": "🔴 PRICING - Reducción de Tarifa",
                "prioridad": "ALTA",
                "canal": "B2C",
                "insight": f"Tu tarifa promedio está {pricing_b2c['var_promedio']:.1%} por encima del mercado",
                "accion": f"Considera reducir tarifas en un {min(pricing_b2c['var_promedio'], 0.15):.1%}",
                "impacto": "Mayor visibilidad y conversión en B2C"
            })
    
    # Disponibilidad
    if 'error' not in demand:
        if demand['lost_rate'] > 0.3:
            recommendations.append({
                "tipo": "🔴 DISPONIBILIDAD - Oportunidad Crítica",
                "prioridad": "CRÍTICA",
                "canal": "Todos",
                "insight": f"Perdiendo {demand['lost_rate']:.1%} de búsquedas por falta de disponibilidad ({demand['lost_requests']:,.0f} requests)",
                "accion": f"Aumenta inventario disponible en sistema",
                "impacto": f"Recuperación potencial de hasta {demand['lost_requests'] * 0.005:,.0f} órdenes"
            })
        
        if len(demand['top_lost_nationalities']) > 0:
            top_nat = demand['top_lost_nationalities'][0]
            if top_nat['lost_requests'] > 1000:
                recommendations.append({
                    "tipo": "🟡 DISPONIBILIDAD - Segmento Específico",
                    "prioridad": "ALTA",
                    "canal": f"Nacionalidad: {top_nat['nationality']}",
                    "insight": f"Perdiste {top_nat['lost_requests']:,.0f} requests del mercado {top_nat['nationality']}",
                    "accion": f"Prioriza disponibilidad para este mercado",
                    "impacto": "Mercado con alta demanda insatisfecha"
                })
    
    return recommendations

# UI PRINCIPAL
st.title("🏨 Agente de Optimización Hotelera")
st.markdown("**Recupera requests perdidos con decisiones inteligentes de pricing y disponibilidad**")

# Sidebar - Selección de hotel
st.sidebar.header("Selecciona tu Hotel")
hoteles = df_hound[['Oid', 'Nombre_Hotel']].drop_duplicates()
hotel_options = {row['Nombre_Hotel']: row['Oid'] for _, row in hoteles.iterrows()}

selected_hotel_name = st.sidebar.selectbox(
    "Hotel:",
    options=list(hotel_options.keys())
)
selected_hotel_id = str(hotel_options[selected_hotel_name])

# Modo de vista
view_mode = st.sidebar.radio(
    "Modo de Vista:",
    ["💬 Chat con Agente", "📊 Dashboard Completo"]
)

if view_mode == "💬 Chat con Agente":
    st.header(f"💬 Chat - {selected_hotel_name}")
    
    # Mensajes predefinidos
    st.markdown("**Preguntas sugeridas:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("¿Cómo está mi competitividad?"):
            st.session_state.query = "competitividad"
    with col2:
        if st.button("¿Cuántos requests estoy perdiendo?"):
            st.session_state.query = "requests_perdidos"
    with col3:
        if st.button("Dame recomendaciones"):
            st.session_state.query = "recomendaciones"
    
    # Respuestas del agente
    if 'query' in st.session_state:
        query = st.session_state.query
        
        st.markdown("---")
        
        if query == "competitividad":
            st.markdown("### 📊 Análisis de Competitividad")
            
            pricing_b2b = get_pricing_competitiveness(selected_hotel_name, 'B2B')
            pricing_b2c = get_pricing_competitiveness(selected_hotel_name, 'B2C')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Precio Promedio B2B", f"${pricing_b2b['precio_promedio_pam']:,.0f}")
                st.metric("Variación vs Mercado B2B", f"{pricing_b2b['var_promedio']:+.1%}")
            
            with col2:
                st.metric("Precio Promedio B2C", f"${pricing_b2c['precio_promedio_pam']:,.0f}")
                st.metric("Variación vs Mercado B2C", f"{pricing_b2c['var_promedio']:+.1%}")
            
            if pricing_b2b['var_promedio'] > 0:
                st.warning(f"⚠️ Estás {pricing_b2b['var_promedio']:.1%} MÁS CARO que el mercado en B2B")
            else:
                st.success(f"✅ Estás {abs(pricing_b2b['var_promedio']):.1%} MÁS BARATO que el mercado en B2B")
        
        elif query == "requests_perdidos":
            st.markdown("### 📉 Análisis de Requests Perdidos")
            
            demand = get_demand_analysis(selected_hotel_id)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Requests", f"{demand['total_requests']:,.0f}")
            col2.metric("Requests Perdidos", f"{demand['lost_requests']:,.0f}")
            col3.metric("Tasa de Pérdida", f"{demand['lost_rate']:.1%}")
            
            st.markdown("#### 🌍 Top Nacionalidades con Demanda Insatisfecha")
            nat_df = pd.DataFrame(demand['top_lost_nationalities'][:5])
            st.dataframe(nat_df[['nationality', 'lost_requests', 'total_requests']], use_container_width=True)
        
        elif query == "recomendaciones":
            st.markdown("### 💡 Recomendaciones Personalizadas")
            
            recs = get_recommendations(selected_hotel_name, selected_hotel_id)
            
            for rec in recs:
                with st.expander(f"{rec['tipo']} - Prioridad: {rec['prioridad']}", expanded=True):
                    st.markdown(f"**Canal:** {rec['canal']}")
                    st.markdown(f"**Insight:** {rec['insight']}")
                    st.markdown(f"**Acción Recomendada:** {rec['accion']}")
                    st.markdown(f"**Impacto Esperado:** {rec['impacto']}")

else:  # Dashboard Completo
    st.header(f"📊 Dashboard - {selected_hotel_name}")
    
    # KPIs principales
    demand = get_demand_analysis(selected_hotel_id)
    pricing_b2b = get_pricing_competitiveness(selected_hotel_name, 'B2B')
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", f"{demand['total_requests']:,.0f}")
    col2.metric("Tasa Disponibilidad", f"{demand['availability_rate']:.1%}")
    col3.metric("Conversión", f"{demand['conversion_rate']:.2%}")
    col4.metric("Var vs Mercado", f"{pricing_b2b['var_promedio']:+.1%}")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribución de Requests")
        fig = go.Figure(data=[go.Pie(
            labels=['Con Disponibilidad', 'Sin Disponibilidad'],
            values=[demand['total_availability'], demand['lost_requests']],
            marker_colors=['#27ae60', '#e74c3c']
        )])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top Mercados con Demanda Insatisfecha")
        nat_df = pd.DataFrame(demand['top_lost_nationalities'][:8])
        fig = px.bar(nat_df, x='lost_requests', y='nationality', orientation='h',
                     color_discrete_sequence=['#9b59b6'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Recomendaciones
    st.markdown("---")
    st.markdown("### 💡 Recomendaciones Prioritarias")
    
    recs = get_recommendations(selected_hotel_name, selected_hotel_id)
    for rec in recs[:3]:
        with st.expander(f"{rec['tipo']}", expanded=True):
            st.markdown(f"**{rec['insight']}**")
            st.markdown(f"✅ {rec['accion']}")
