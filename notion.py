import streamlit as st
from notion_client import Client
import pandas as pd

# Configuración de la integración con Notion
NOTION_KEY = "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"
DATABASE_ID = "1ad6f68ec3054ac5b8842592263c1c29"  # ID de la base de datos

# Inicializar el cliente de Notion
notion = Client(auth=NOTION_KEY)

# Función para obtener elementos de la base de datos
def get_database_items(database_id):
    """
    Consulta una base de datos de Notion y retorna los datos en forma de lista.
    """
    try:
        response = notion.databases.query(database_id=database_id)
        results = response.get('results', [])
        items = []
        for result in results:
            properties = result['properties']
            row = {}
            for key, value in properties.items():
                if value['type'] == 'title':
                    row[key] = value['title'][0]['plain_text'] if value['title'] else ""
                elif value['type'] == 'rich_text':
                    row[key] = value['rich_text'][0]['plain_text'] if value['rich_text'] else ""
                elif value['type'] == 'select':
                    row[key] = value['select']['name'] if value['select'] else ""
                elif value['type'] == 'multi_select':
                    row[key] = ", ".join([v['name'] for v in value['multi_select']])
                elif value['type'] == 'date':
                    row[key] = value['date']['start'] if value['date'] else ""
                elif value['type'] == 'number':
                    row[key] = value['number']
                elif value['type'] == 'checkbox':
                    row[key] = value['checkbox']
                else:
                    row[key] = ""
            items.append(row)
        return items
    except Exception as e:
        st.error(f"Error al consultar la base de datos: {e}")
        return []

# Streamlit App
st.title("Dashboard de Productos")
st.write("Este dashboard muestra los datos de la base de datos **Productos** en Notion.")

# Consultar datos de la base de datos
st.subheader("Datos de la base de datos")
items = get_database_items(DATABASE_ID)

if items:
    # Convertir los datos en un DataFrame
    df = pd.DataFrame(items)

    # Mostrar tabla completa
    st.write("### Tabla completa")
    st.dataframe(df)

    # Filtros dinámicos en la barra lateral
    st.sidebar.header("Filtros dinámicos")
    for column in df.columns:
        if df[column].nunique() < 10:  # Aplicar filtros para columnas con pocos valores únicos
            selected_values = st.sidebar.multiselect(f"Filtrar por {column}", df[column].unique())
            if selected_values:
                df = df[df[column].isin(selected_values)]

    # Mostrar tabla filtrada
    st.write("### Tabla filtrada")
    st.dataframe(df)
else:
    st.write("No se encontraron datos en la base de datos seleccionada.")
