import streamlit as st
from notion_client import Client
import pandas as pd

# Configuración de la integración con Notion
NOTION_KEY = "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"
notion = Client(auth=NOTION_KEY)

# Función para obtener elementos de una base de datos
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

# Función para obtener todas las bases de datos accesibles
def list_databases():
    try:
        response = notion.search(filter={"property": "object", "value": "database"})
        databases = response.get('results', [])
        return [{"id": db['id'], "name": db['title'][0]['plain_text'] if db['title'] else "Sin título"} for db in databases]
    except Exception as e:
        st.error(f"Error al listar las bases de datos: {e}")
        return []

# Streamlit App
st.title("Dashboard conectado a Notion")
st.write("Conéctate y explora las bases de datos de tu Notion.")

# Listar bases de datos disponibles
st.sidebar.header("Selecciona una base de datos")
databases = list_databases()

if databases:
    db_options = {db['name']: db['id'] for db in databases}
    selected_db = st.sidebar.selectbox("Bases de datos disponibles", list(db_options.keys()))
    database_id = db_options[selected_db]

    # Consultar datos de la base de datos seleccionada
    st.subheader(f"Datos de la base de datos: {selected_db}")
    items = get_database_items(database_id)

    if items:
        df = pd.DataFrame(items)
        st.dataframe(df)

        # Filtros dinámicos
        st.sidebar.header("Filtros")
        for column in df.columns:
            if df[column].nunique() < 10:  # Aplicar filtros para columnas con pocos valores únicos
                selected_values = st.sidebar.multiselect(f"Filtrar por {column}", df[column].unique())
                if selected_values:
                    df = df[df[column].isin(selected_values)]

        # Mostrar tabla filtrada
        st.subheader("Datos filtrados")
        st.dataframe(df)
    else:
        st.write("No se encontraron datos en la base de datos seleccionada.")
else:
    st.write("No se encontraron bases de datos disponibles para la integración.")