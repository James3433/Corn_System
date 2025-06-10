import base64
import streamlit as st
import httpx

from supabase_connect import get_user_id, insert_comments, get_all_comments, get_user_name

def app(): 

    @st.cache_data
    def get_img_as_base64(file):
        with open (file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    img_1 = get_img_as_base64("images/farmer_PNG.png")
    img_2 = get_img_as_base64("images/trader_PNG.png")
    img_3 = get_img_as_base64("images/user.png")

    main_user_id = st.session_state.get('user_id', 1)
    fname = st.session_state.get('fname', 'First Name')
    lname = st.session_state.get('lname', 'Last Name')
    user_type = st.session_state.get('user_type', 'User Type')

    user_type_num = {1: "Farmer", 2: "Trader", 3: "Consumer", 4: "Admin"}
    user_type_pic = {1: img_1, 2: img_2, 3: img_3, 4: img_3}

    img = user_type_pic[user_type]
    user_type = user_type_num[user_type]



    # Clear comments_input BEFORE rendering widgets if flag exists
    if "clear_comments" in st.session_state:
        st.session_state.comments_input = ""  # Reset the input
        del st.session_state.clear_comments  # Remove flag


    # Initialize session state for comments if not already set
    if "comments_input" not in st.session_state:
        st.session_state.comments_input = ""


    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(f"""
            <style>
                [data-testid="stVerticalBlockBorderWrapper"] {{
                    background-color: #66CC91;
                    width: 100%;
                    height: 110%; 
                    border-radius: 10px;
                    padding: 1% 5%;
                }}

                .comment_box{{
                    border-radius: 10px;
                    background-color: #389961;
                    padding: 1% 5%;
                    margin-bottom: 2%;
                }}
                .comment_box p{{
                    margin-left: 40px;
                }}
                .comment_box st-emotion-cache-asc41u e1nzilvr2 h5{{
                    padding: 0px;
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
                    <img src="data:image/png;base64,{img}" alt="A beautiful landscape" width="40px" height="40px">
                    <h4>{fname} {lname} ({user_type})</h4>
                </div>
                <h4>Comments</h4>
            </div>
    """, unsafe_allow_html=True)

    try:
        # In your Streamlit app or console
        comments = get_all_comments()
        comments_count = len(comments)
    
    except httpx.RequestError as e:  # Catch connection & request-related errors
        st.error("Connection error: Unable to connect to the server. Please try again later.")
        if st.button("Reload"):
            st.rerun()
        st.stop()  # Prevents further execution

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        if st.button("Reload"):
            st.rerun()
        st.stop()  # Prevents further execution

    with st.expander(f"Comments ({comments_count})"):
        if comments and len(comments) > 0:
            for user_id, comments in comments:
                fname, lname, user_type = get_user_name(user_id)
                img = user_type_pic[user_type]
                user_type = user_type_num[user_type]
                st.markdown(f"""
                <div class="comment_box">
                    <div class="user_name">
                        <img src="data:image/png;base64,{img}" alt="A beautiful landscape" width="30px" height="30px">
                        <h5>{fname} {lname} ({user_type})</h5>
                    </div>
                    <p>{comments}</p>
                </div>
        """, unsafe_allow_html=True)
        else:
            st.write("No comments found.")

    st.text_area(label=" ", placeholder="Write your Comments Here.....", key="comments_input")

    if st.button("SEND"):
        try:
            # Check if comments are empty
            if not comments.strip():  # Check if comments is empty or only whitespace
                st.error("Please input comments first.")  # Show error message
            else:
                # Proceed to insert comments into the database
                response = insert_comments(main_user_id, st.session_state.comments_input)
                
                if response.data:  # Successful insertion
                    st.success("Comments added successfully!")

                    # Set flag to trigger clear in next run
                    st.session_state.clear_comments = True

                    st.rerun()
                elif response.error:
                    st.error("An error occurred while adding your comments.")

        except httpx.RequestError as e:  # Catch connection & request-related errors
            st.error("Connection error: Unable to connect to the server. Please try again later.")
            if st.button("Reload"):
                st.rerun()
            st.stop()  # Prevents further execution

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            if st.button("Reload"):
                st.rerun()
            st.stop()  # Prevents further execution

