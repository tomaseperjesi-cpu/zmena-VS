import streamlit as st
import xml.etree.ElementTree as ET
import io

st.set_page_config(page_title="Úprava variabilných symbolov", layout="centered")

st.title("Hromadná úprava variabilných symbolov (POHODA)")
st.write("Nahrajte váš exportný XML/TXT súbor z Pohody. Aplikácia podľa nastavení upraví variabilné symboly.")

# Nastavenia v bočnom paneli
st.sidebar.header("Nastavenia fakturačných radov")
st.sidebar.write("Zadajte text, ktorý identifikuje fakturačný rad v čísle faktúry (napr. VFB).")

# Konfigurácia pravidiel
series_1 = st.sidebar.text_input("Identifikátor pre radu 1 (pridáva 1)", value="VFB")
prefix_1 = st.sidebar.text_input("Číslo, ktoré sa pridá na začiatok (Rada 1)", value="1")

series_2 = st.sidebar.text_input("Identifikátor pre radu 2 (pridáva 2)", value="VFD")
prefix_2 = st.sidebar.text_input("Číslo, ktoré sa pridá na začiatok (Rada 2)", value="2")

st.info("💡 Faktúry z rady VFA (alebo iné nevyplnené vyššie) ostanú bez zmeny.")

uploaded_file = st.file_uploader("Vyberte súbor (XML alebo TXT)", type=['xml', 'txt'])

if uploaded_file is not None:
    # Načítanie obsahu
    content = uploaded_file.getvalue()
    
    try:
        # POHODA XML využíva menné priestory (namespaces), tie musíme zaregistrovať, aby ostali zachované
        namespaces = {
            'dat': 'http://www.stormware.cz/schema/version_2/data.xsd',
            'inv': 'http://www.stormware.cz/schema/version_2/invoice.xsd',
            'typ': 'http://www.stormware.cz/schema/version_2/type.xsd',
            'rsp': 'http://www.stormware.cz/schema/version_2/response.xsd',
            'rdc': 'http://www.stormware.cz/schema/version_2/documentresponse.xsd',
            'ftr': 'http://www.stormware.cz/schema/version_2/filter.xsd',
            'lst': 'http://www.stormware.cz/schema/version_2/list.xsd'
        }
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)

        # Parsovanie XML
        tree = ET.parse(io.BytesIO(content))
        root = tree.getroot()
        
        modified_count = 0
        
        # Prechádzame všetky faktúry v súbore
        for invoice in root.findall('.//inv:invoice', namespaces):
            header = invoice.find('inv:invoiceHeader', namespaces)
            if header is not None:
                # Nájdeme číslo faktúry a variabilný symbol
                number_requested = header.find('./inv:number/typ:numberRequested', namespaces)
                sym_var = header.find('inv:symVar', namespaces)
                
                if number_requested is not None and number_requested.text and sym_var is not None and sym_var.text:
                    inv_number = number_requested.text
                    current_sym_var = sym_var.text
                    
                    # Logika úpravy
                    if series_1 and series_1 in inv_number:
                        sym_var.text = prefix_1 + current_sym_var
                        modified_count += 1
                    elif series_2 and series_2 in inv_number:
                        sym_var.text = prefix_2 + current_sym_var
                        modified_count += 1
        
        # Uloženie upraveného XML do pamäte s pôvodným kódovaním (Windows-1250)
        output = io.BytesIO()
        tree.write(output, encoding='Windows-1250', xml_declaration=True)
        output.seek(0)
        
        st.success(f"Súbor bol úspešne spracovaný! Počet zmenených variabilných symbolov: {modified_count}")
        
        st.download_button(
            label="Stiahnuť upravený súbor",
            data=output,
            file_name="Upravene_Faktury.xml",
            mime="application/xml"
        )
        
    except Exception as e:
        st.error(f"Nastala chyba pri spracovaní XML súboru: {e}")
