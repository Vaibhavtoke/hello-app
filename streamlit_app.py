import streamlit as st
import requests
from streamlit_option_menu import option_menu
import mysql.connector
import pandas as pd
import plotly.express as px

# Establish the MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="vaib163t@",
    database="crud_new1",
)

# Create a cursor object
mycursor = mydb.cursor()

# Function to post data to the webhook
WEBHOOK_URL = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjYwNTZjMDYzNjA0MzY1MjZhNTUzZDUxMzAi_pc"

def post_to_webhook(**data):
    response = requests.post(WEBHOOK_URL, json=data)
    return response

# Function to display the login page
def login():
    st.title("Login Page")

    # Input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check for correct username and password
        if username == "Vaibhav Toke" and password == "vaib163t@":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "admin"
            st.success("Logged in as Admin!")
        elif username == "prestigealumini@gmail.com" and password == "alumini":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "alumini"
            st.success("Logged in as Alumni!")
        elif username == "prestigeteacher@gmail.com" and password == "teacher":
            st.session_state["logged_in"] = True
            st.session_state["role"] = "teacher"
            st.success("Logged in as Teacher!")
        else:
            st.error("Incorrect username or password. Please try again.")

# Main app function with the option menu
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        selected = option_menu(
            menu_title=None,  # required
            options=["Dashboard", "Feedback Form", "CRUD Operations"],  # required
            icons=["bar-chart-fill", "chat-fill", "tools"],  # optional icons
            menu_icon="cast",  # optional
            default_index=0,  # which tab to start with
            orientation="horizontal"
        )

        if selected == "Dashboard":
            dashboard()
        elif selected == "Feedback Form":
            feedback_form()
        elif selected == "CRUD Operations":
            crud_operations()

# Dashboard tab
def dashboard():
    st.title("Dashboard")

    # ---- Fetch Data from MySQL ----
    @st.cache_data
    def get_data_from_mysql():
        query = "SELECT * FROM users"
        mycursor.execute(query)
        result = mycursor.fetchall()

        if len(result) == 0:
            st.error("No data found in the database.")
            return pd.DataFrame()

        column_names = [i[0] for i in mycursor.description]
        df = pd.DataFrame(result, columns=column_names)
        return df

    df = get_data_from_mysql()

    # Show data
    st.write(df.columns)
    st.write(df)

    if df.empty:
        st.warning("The table is empty. Please add some data.")
        st.stop()

    # Sidebar filters
    st.sidebar.header("Please Filter Here:")
    user_id = st.sidebar.multiselect("Select User ID:", options=df["id"].unique(), default=df["id"].unique())
    name_filter = st.sidebar.multiselect("Select User Name:", options=df["name"].unique(), default=df["name"].unique())
    
    df_selection = df[(df["id"].isin(user_id)) & (df["name"].isin(name_filter))]

    if df_selection.empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

    # KPIs
    total_users = df_selection["id"].nunique()
    unique_email_domains = df_selection["email"].apply(lambda x: x.split('@')[1]).nunique()
    average_name_length = round(df_selection["name"].apply(len).mean(), 1)

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Total Users:")
        st.subheader(f"{total_users}")
    with middle_column:
        st.subheader("Unique Email Domains:")
        st.subheader(f"{unique_email_domains}")
    with right_column:
        st.subheader("Average Name Length:")
        st.subheader(f"{average_name_length} characters")

    st.markdown("---")

    # Bar charts
    users_by_name = df_selection.groupby(by=["name"])[["id"]].count().sort_values(by="id")
    fig_user_count = px.bar(
        users_by_name,
        x="id",
        y=users_by_name.index,
        orientation="h",
        title="<b>Users by Name</b>",
        color_discrete_sequence=["#0083B8"] * len(users_by_name),
        template="plotly_white",
    )
    fig_user_count.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))

    email_domains = df_selection["email"].apply(lambda x: x.split('@')[1]).value_counts()
    fig_email_domains = px.bar(
        email_domains,
        x=email_domains.index,
        y=email_domains.values,
        title="<b>Email Domains Count</b>",
        color_discrete_sequence=["#0083B8"] * len(email_domains),
        template="plotly_white",
    )
    fig_email_domains.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(tickmode="linear"), yaxis=dict(showgrid=False))

    left_column, right_column = st.columns(2)
    left_column.plotly_chart(fig_user_count, use_container_width=True)
    right_column.plotly_chart(fig_email_domains, use_container_width=True)

# Feedback form tab
def feedback_form():
    st.title("🎬 Submit Your Idea about Sangam")
    st.markdown("Feedback Form. Give us feedback about our Sangam webapp.")

    with st.form(key="idea_form"):
        name = st.text_input("Name (optional)", placeholder="Your Name")
        email = st.text_input("Email (optional)", placeholder="Your Email")
        video_idea = st.text_area("Video Idea", placeholder="Describe your idea...")

        submit_button = st.form_submit_button(label="Submit Idea 🚀")

        if submit_button:
            if not video_idea.strip():
                st.error("Please enter a video idea. 💡")
                st.stop()

            data = {"name": name, "email": email, "video_idea": video_idea}
            response = post_to_webhook(**data)
            if response.status_code == 200:
                st.success("Thanks for your submission! 🌟")
            else:
                st.error("There was an error. Please try again. 🛠")

# CRUD Operations tab
def crud_operations():
    st.title("Alumni Records")
    
    # Get user role from session
    role = st.session_state.get("role", "")

    # Filter allowed operations based on role
    if role == "admin":
        allowed_operations = ["Create", "Read", "Update", "Delete"]
    elif role == "alumini":
        allowed_operations = ["Create", "Update"]
    elif role == "teacher":
        allowed_operations = ["Read"]
    else:
        allowed_operations = []

    if not allowed_operations:
        st.error("You do not have permission to perform any operations.")
        return

    # Operation selection based on role
    operation = st.sidebar.selectbox("Select an Operation", allowed_operations)

    if operation == "Create":
        st.subheader("Create a Record")
        name = st.text_input("Enter Name")
        email = st.text_input("Enter Email")
        if st.button("Create"):
            sql = "insert into users(name, email) values(%s, %s)"
            val = (name, email)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Record Created Successfully!!!")
    elif operation == "Read":
        st.subheader("Read a Record")
        mycursor.execute("select * from users")
        result = mycursor.fetchall()
        for row in result:
            st.write(row)
    elif operation == "Update":
        st.subheader("Update a Record")
        id = st.number_input("Enter ID")
        name = st.text_input("Enter New Name")
        email = st.text_input("Enter New Email")
        if st.button("Update"):
            sql = "update users set name = %s, email = %s where id = %s"
            val = (name, email, id)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Record Updated Successfully")
    elif operation == "Delete":
        st.subheader("Delete a Record")
        id = st.number_input("Enter ID")
        if st.button("Delete"):
            sql = "delete from users where id = %s"
            val = (id,)
            mycursor.execute(sql, val)
            mydb.commit()
            st.success("Record Deleted Successfully")

if __name__ == "__main__":
    main()
