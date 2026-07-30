import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Assistente SOAP",
    page_icon="🩺",
    layout="centered"
)

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔒 Acesso Restrito")
        st.text_input("Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔒 Acesso Restrito")
        st.text_input("Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
        st.error("😕 Senha incorreta.")
        return False
    else:
        return True

if not check_password():
    st.stop()

st.title("🩺 Assistente SOAP Clínico")
st.caption("Cole a transcrição da consulta para gerar a estrutura SOAP e Informações.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

transcricao = st.text_area(
    "Transcrição da Consulta:",
    placeholder="Cole aqui o texto copiado do gravador do iPhone...",
    height=200
)

if "resultado_so" not in st.session_state:
    st.session_state["resultado_so"] = ""

if st.button("Gerar Estrutura e Informações", type="primary", use_container_width=True):
    if not transcricao.strip():
        st.warning("Por favor, cole a transcrição antes de gerar.")
    else:
        with st.spinner("Analisando e estruturando os dados..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Você é um assistente médico especialista em Medicina de Família e Psiquiatria. "
                                "A partir da transcrição de consulta fornecida, extraia e estruture estritamente nos três blocos abaixo. "
                                "Mantenha tom técnico, objetivo e clínico. Não invente dados; se algo não estiver na transcrição, escreva 'não informado'. "
                                "Se houver ideação suicida ativa ou plano, inclua imediatamente recomendação de busca de emergência. "
                                "Ignore trechos irrelevantes (conversas sociais, piadas) a menos que indiquem humor ou risco.\n\n"
                                "Formate a saída exatamente assim:\n\n"
                                "### Subjetivo (S)\n"
                                "- Queixa principal: ...\n"
                                "- História da doença atual: ...\n"
                                "- Histórico de doenças: ...\n"
                                "- Sintomas relevantes: ...\n"
                                "- Ideação suicida: presente/ausente; detalhes se presentes.\n\n"
                                "### Objetivo (O)\n"
                                "- Sinais vitais relatados/examinados: ...\n"
                                "- Achados do exame físico narrados: ...\n"
                                "- Exames solicitados/valores objetivos citados: ...\n\n"
                                "### Informações (I)\n"
                                "- Idade; \n"
                                "- estado civil; \n"
                                "- profissão; \n"
                                "- filhos: ...\n"
                                "- Histórico familiar relevante: ...\n"
                                "- Uso de substâncias: álcool, tabaco, benzodiazepínicos (quantidade/frequência)\n"
                                "- Impacto funcional e social: ..."
                            )
                        },
                        {
                            "role": "user",
                            "content": transcricao
                        }
                    ],
                    temperature=0.2,
                    max_tokens=2000,
                    top_p=0.9,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                
                st.session_state["resultado_so"] = response.choices[0].message.content
                st.success("Prontuário estruturado com sucesso!")
                st.toast("Lembre de tomar Água! 💧", icon="🚰")
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar: {e}")

# Exibe o resultado limpo e o botão de download
if st.session_state["resultado_so"]:
    st.markdown(st.session_state["resultado_so"])
    
    st.divider()
    
    st.download_button(
        label="📥 Baixar Prontuário (.txt)",
        data=st.session_state["resultado_so"],
        file_name="prontuario_soap.txt",
        mime="text/plain",
        use_container_width=True
    )