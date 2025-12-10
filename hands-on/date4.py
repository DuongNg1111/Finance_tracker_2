import streamlit as st

st.title("Mongo Class Day4")
st.text("Run command: streamlit run <script_name>") #TODO: convert <script_name> to code

#TODO:
st.text("To start streamlit app: ")
st.code("streamlit run <script_name>", language='bash')
        
#Expander and containers
st.subheader("Expander")
with st.expander("Click to expand"):
    st.write("This is content hidden by default!")
    st.code("print('Hello World!')", language='python')

#Progress and Status
st.subheader("Progress and Status")

#progress bar:
progress = st.slider("Progress", 0, 100, 50)
st.progress(progress)

#spinner
if st.button("Show Spinner"):
    with st.spinner("Loading..."):
        import time
        time.sleep(2)
    st.success("Data loaded!")

# st.divider()

#Metric (cards)
st.subheader("📊 Metric (dashboard cards)")

#single metric
st.metric("🌡️ Temperature",
            value="25 °C",
            delta="1.5 °C",
            delta_color="normal"
        )

st.markdown("Temperature in cities")

#multiple metrics: METHOD 1
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ho Chi Minh", "35 °C", "3 °C")
with col2:
    st.metric("Ha Noi", "28 °C", "-2 °C")
with col3:
    st.metric("Hue", "30 °C", "1 °C")

st.divider()
#multiple metrics: METHOD 2
# CITIES = ["Ho Chi Minh", "Ha Noi", "Hue"]
# temps = [35, 28, 30]
# deltas = [3, -2, 1]

# cols = st.columns(len(CITIES))

# for index in range (len(CITIES)):
#     with cols[index]:
#         st.metric(
#             CITIES[index],
#             f"{temps[index]} °C",
#             f"{deltas[index]} °C"
#         )

#sidebar
st.header("⚙️ Sidebar")
st.sidebar.title("🏦 Management")
st.sidebar.text("Put your settings here!")

#option
sidebar_option = st.sidebar.selectbox(
    "Select an option",
    ["3 months", "6 months", "1 year"]
)

st.write(f"Sidebar option selected: **{sidebar_option}**")

st.divider()

#form
st.subheader("📝 Form")
st.write("Subit your passport information")
with st.form("my_form"):
    st.write("Passport Submission Forrm")
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    age = st.number_input("Age", min_value=0, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    #Form submit button
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("Form submitted successfully!")
        st.write("Your passport information:")
        st.json({
            "name": name,
            "email": email,
            "age": age,
            "gender": gender
        })
        
st.divider()