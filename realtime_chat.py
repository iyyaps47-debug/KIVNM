# realtime_chat.py - FINAL WORKING VERSION
# NO st.rerun() at end - prevents set_page_config() being called again
# Uses simple polling without full page rerun

import streamlit as st
import time
from datetime import datetime

def get_chat_history(user_id: str, limit: int = 100):
    """Fetch chat history using lazy import"""
    try:
        import sys
        if 'app1_imp' in sys.modules:
            app_module = sys.modules['app1_imp']
            if hasattr(app_module, 'get_chat_history'):
                return app_module.get_chat_history(user_id, limit=limit)
        
        from app1_imp import get_chat_history as app_get_chat_history
        return app_get_chat_history(user_id, limit=limit)
    except Exception as e:
        return []


def format_timestamp(timestamp):
    """Convert timestamp to readable format"""
    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        now = datetime.now()
        if timestamp.date() == now.date():
            return timestamp.strftime("%H:%M:%S")
        else:
            return timestamp.strftime("%d/%m/%Y %H:%M")
    except:
        return str(timestamp)


# ============ MAIN FUNCTION - NO st.rerun() ============

def render_chat_history_realtime_simple():
    """
    Real-time chat history display WITHOUT st.rerun()
    This prevents the set_page_config() error!
    """
    st.subheader("💬 Chat History (Live)")
    
    # Control panel
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        auto_refresh = st.checkbox("🔄 Auto-Refresh", value=True, key="auto_refresh_chat")
    
    with col2:
        if st.button("↻ Manual Refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        st.caption("Updates every 2s")
    
    st.markdown("---")
    
    try:
        user_id = st.session_state.user.id
        chat_history = get_chat_history(user_id)
        
        if not chat_history:
            st.info("💭 No chat history yet. Start a conversation with the chatbot!")
        else:
            # Display messages (last 20)
            for chat in reversed(chat_history[-20:]):
                # User message
                st.markdown(f"""
                    <div style="
                        background: #EFF6FF;
                        padding: 1rem;
                        border-radius: 0.75rem;
                        margin-bottom: 0.5rem;
                        border-left: 4px solid #3B82F6;
                    ">
                        <strong style="color: #1E40AF;">👤 You</strong><br>
                        <span style="color: #1E293B;">{chat.get('message', '')}</span><br>
                        <small style="color: #64748B; margin-top: 0.5rem; display: block;">
                            {format_timestamp(chat.get('timestamp', datetime.now()))}
                        </small>
                    </div>
                """, unsafe_allow_html=True)
                
                # Bot response
                st.markdown(f"""
                    <div style="
                        background: #F0FDF4;
                        padding: 1rem;
                        border-radius: 0.75rem;
                        margin-bottom: 1rem;
                        border-left: 4px solid #10B981;
                    ">
                        <strong style="color: #065F46;">🤖 LearnMate Bot</strong><br>
                        <span style="color: #1E293B;">{chat.get('response', '')}</span><br>
                        <small style="color: #64748B; margin-top: 0.5rem; display: block;">
                            {format_timestamp(chat.get('timestamp', datetime.now()))}
                        </small>
                    </div>
                """, unsafe_allow_html=True)
        
        # Show status
        st.success(
            f"✅ Last updated: {datetime.now().strftime('%H:%M:%S')} | "
            f"Messages: {len(chat_history)}"
        )
        
        # IMPORTANT: NO st.rerun() here!
        # If auto_refresh is enabled, user needs to manually refresh or wait for browser refresh
        if auto_refresh:
            # Use client-side refresh via HTML/JavaScript
            st.markdown("""
                <script>
                setTimeout(function() {
                    location.reload();
                }, 2000);
                </script>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Cannot load chat history: {str(e)}")


# ============ ADMIN FUNCTION ============

def render_admin_chat_monitoring():
    """Admin chat monitoring"""
    st.subheader("💬 Real-Time Chat Monitoring")
    
    try:
        import sys
        
        # Get db module
        if 'app1_imp' in sys.modules:
            app_module = sys.modules['app1_imp']
            db = app_module.db
        else:
            from app1_imp import db
        
        users = db.get_all_users()
        
        if not users:
            st.info("No users found")
            return
        
        # User selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_user = st.selectbox(
                "Select user to monitor",
                options=[f"{u.name} ({u.email})" for u in users],
                key="admin_user_select"
            )
        
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-Refresh", value=True, key="admin_auto_refresh")
        
        with col3:
            if st.button("↻ Refresh Now", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # Extract user
        selected_name = selected_user.split(" (")[0]
        user = next((u for u in users if u.name == selected_name), None)
        
        if not user:
            st.error("User not found")
            return
        
        # Fetch and display
        chat_history = get_chat_history(user.id)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", len(chat_history))
        with col2:
            st.metric("User Name", user.name)
        with col3:
            st.metric("User Email", user.email)
        
        st.markdown("---")
        
        # Messages
        if not chat_history:
            st.info(f"No chat history for {user.name}")
        else:
            for chat in reversed(chat_history[-30:]):
                col1, col2 = st.columns([1, 10])
                
                with col1:
                    st.markdown("👤")
                with col2:
                    st.markdown(f"""
                        <div style="background: #DBEAFE; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            <strong>User Message</strong><br>
                            {chat.get('message', '')}<br>
                            <small style="opacity: 0.7;">{format_timestamp(chat.get('timestamp', datetime.now()))}</small>
                        </div>
                    """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.markdown("🤖")
                with col2:
                    st.markdown(f"""
                        <div style="background: #DCFCE7; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <strong>Bot Response</strong><br>
                            {chat.get('response', '')}<br>
                            <small style="opacity: 0.7;">{format_timestamp(chat.get('timestamp', datetime.now()))}</small>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Status
        st.success(f"✅ Updated: {datetime.now().strftime('%H:%M:%S')} | User: {user.name}")
        
        # Auto-refresh via client-side
        if auto_refresh:
            st.markdown("""
                <script>
                setTimeout(function() {
                    location.reload();
                }, 2000);
                </script>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ============ CACHED VERSION ============

@st.cache_data(ttl=2)
def get_chat_history_cached(user_id: str, limit: int = 50):
    """Cached version"""
    return get_chat_history(user_id, limit=limit)


def render_chat_history_optimized():
    """Optimized with caching (NO st.rerun)"""
    st.subheader("💬 Chat History")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("🟢 Live updates enabled")
    with col2:
        st.caption("Refresh: 2 seconds")
    with col3:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    try:
        user_id = st.session_state.user.id
        chat_history = get_chat_history_cached(user_id)
        
        if not chat_history:
            st.info("No messages yet")
        else:
            with st.expander(f"Chat History ({len(chat_history)} messages)", expanded=True):
                for chat in reversed(chat_history[-20:]):
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        st.markdown("👤")
                    with col2:
                        st.markdown("**You**")
                        st.write(chat.get('message', ''))
                        st.caption(format_timestamp(chat.get('timestamp', datetime.now())))
                    
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        st.markdown("🤖")
                    with col2:
                        st.markdown("**Bot**")
                        st.write(chat.get('response', ''))
                        st.caption(format_timestamp(chat.get('timestamp', datetime.now())))
                    
                    st.divider()
        
        # Auto-refresh via client-side (NO st.rerun!)
        st.markdown("""
            <script>
            setTimeout(function() {
                location.reload();
            }, 2000);
            </script>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
