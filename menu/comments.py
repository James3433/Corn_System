import base64
import streamlit as st
from supabase_connect import get_user_id, insert_comments, get_all_comments, get_user_name

def app(): 

    @st.cache_data
    def get_img_as_base64(file):
        with open (file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    img_1 = get_img_as_base64("images/user.png")

    fname = st.session_state.get('fname', 'First Name')
    lname = st.session_state.get('lname', 'Last Name')
    user_type = st.session_state.get('user_type', 'User Type')

    user_type_num = {1: "Farmer", 2: "Trader", 3: "Consumer", 4: "Admin"}

    user_type = user_type_num[user_type]

    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stVerticalBlockBorderWrapper"] {{
                    background-color: #8edd27;;
                    width: 100%;
                    height: 110%; 
                    border-radius: 10px;
                    padding: 1% 5%;
                }}
                .st-emotion-cache-1h9usn1 {{
                    background-color: yellowgreen;
                }}
                .user_name{{
                    display: flex;
                }}
                .user_name img{{
                    margin-right: 10px;
                }}
            </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
            <div class="comments_intro">
                <div class="user_name">
                    <img src="data:image/png;base64,{img_1}" alt="A beautiful landscape" width="40px" height="40px">
                    <h4>{fname} {lname} ({user_type})</h4>
                </div>
                <h4>Comments</h4>
            </div>
    """, unsafe_allow_html=True)

    # In your Streamlit app or console
    comments = get_all_comments()
    comments_count = len(comments)

    user_type_num = {1: "Farmer", 2: "Trader", 3: "Consumer", 4: "Consumer"}

    with st.expander(f"Comments ({comments_count})"):
        if comments and len(comments) > 0:
            for user_id, comments in comments:
                fname, lname, user_type = get_user_name(user_id)
                user_type = user_type_num[user_type]
                st.markdown(f"""
                <div class="comment_box">
                    <div class="user_name">
                        <img src="data:image/png;base64,{img_1}" alt="A beautiful landscape" width="30px" height="30px">
                        <h5>{fname} {lname} ({user_type})</h5>
                    </div>
                    <p>{comments}</p>
                </div>
        """, unsafe_allow_html=True)
        else:
            st.write("No comments found.")

    comments = st.text_area(label=" ", placeholder="Write your Comments Here.....")

    if st.button("SEND"):
        user_id = get_user_id(fname, lname)
        response = insert_comments(user_id, comments)
        if response.data:  # Successful insertion
            st.success("Comments added successfully!")
        elif response.error:
            st.error("There was an issue")
    # st.success(f"user_name: {fname} {lname}")

