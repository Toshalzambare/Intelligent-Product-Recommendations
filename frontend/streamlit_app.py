import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# Configure API URL (adjust if FastAPI is running on a different port/host)
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Intelligent Product Recommendation", layout="wide", page_icon="🛒")

# Utility function to check API health
@st.cache_data(ttl=60)
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Utility function to fetch data
def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching data from backend: {e}")
    return None

def fetch_recommendations(products, min_confidence=0.0, min_lift=0.0):
    try:
        payload = {
            "products": products,
            "min_confidence": min_confidence,
            "min_lift": min_lift
        }
        response = requests.post(f"{API_URL}/recommend", json=payload)
        if response.status_code == 200:
            return response.json().get("recommendations", [])
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
    return []

api_ready = check_api_health()

if not api_ready:
    st.error("Backend API is not running or models are not loaded. Please start the FastAPI server.")
    st.stop()

# Load initial data
with st.spinner("Loading products..."):
    products_data = fetch_data("products")
    product_list = products_data.get("products", []) if products_data else []

st.title("🛒 Intelligent Product Recommendation System")

# Sidebar Navigation
page = st.sidebar.radio("Navigation", [
    "Dashboard", 
    "Product Recommendation", 
    "Market Basket Analyzer", 
    "Association Rule Explorer",
    "Analytics",
    "Algorithm Comparison"
])

if page == "Dashboard":
    st.header("System Dashboard")
    
    analytics = fetch_data("analytics")
    if analytics:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL PRODUCTS", analytics.get("total_products", 0))
        with col2:
            st.metric("FREQUENT ITEMSETS", analytics.get("frequent_itemsets", 0))
        with col3:
            st.metric("ASSOCIATION RULES", analytics.get("total_rules", 0))
    else:
        st.info("No analytics data available.")
        
    st.markdown("---")
    st.markdown("""
    ### About this System
    This system discovers hidden patterns in customer purchasing behavior using unsupervised machine learning.
    Specifically, it leverages **Association Rule Mining** (Apriori and FP-Growth algorithms) to recommend products that are frequently bought together.
    """)

elif page == "Product Recommendation":
    st.header("Single Product Recommendation")
    
    if not product_list:
        st.warning("No products available.")
    else:
        selected_product = st.selectbox("Product:", options=[""] + product_list)
        
        if st.button("Generate Recommendations"):
            if selected_product:
                with st.spinner("Generating recommendations..."):
                    recs = fetch_recommendations([selected_product])
                    
                if recs:
                    st.success("RECOMMENDED PRODUCTS")
                    for rec in recs:
                        st.markdown(f"""
                        <div style='padding: 10px; border: 1px solid #4CAF50; border-radius: 5px; margin-bottom: 10px;'>
                            <h4>{rec['product']}</h4>
                            <p>Confidence: {rec['confidence']:.1%}</p>
                            <p>Lift: {rec['lift']:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No recommendations found for '{selected_product}'.")
            else:
                st.warning("Please select a product.")

elif page == "Market Basket Analyzer":
    st.header("Market Basket Analyzer")
    st.markdown("Select multiple products currently in a user's cart to find recommendations.")
    
    if not product_list:
        st.warning("No products available.")
    else:
        selected_products = st.multiselect("Selected Products:", options=product_list)
        
        if st.button("Analyze Cart"):
            if selected_products:
                st.write(f"The system finds patterns based on: **{' + '.join(selected_products)}**")
                
                with st.spinner("Analyzing..."):
                    recs = fetch_recommendations(selected_products)
                    
                if recs:
                    st.success("RECOMMENDED PRODUCTS")
                    for rec in recs:
                        st.markdown(f"""
                        <div style='padding: 10px; border: 1px solid #2196F3; border-radius: 5px; margin-bottom: 10px;'>
                            <h4>{rec['product']}</h4>
                            <p>Confidence: {rec['confidence']:.1%}</p>
                            <p>Lift: {rec['lift']:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No strong associations found for this specific combination.")
            else:
                st.warning("Please select at least one product.")

elif page == "Association Rule Explorer":
    st.header("Association Rule Explorer")
    
    st.sidebar.subheader("Filters")
    min_support = st.sidebar.slider("Minimum Support", 0.0, 0.5, 0.01, step=0.01)
    min_confidence = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, step=0.05)
    min_lift = st.sidebar.slider("Minimum Lift", 1.0, 10.0, 1.0, step=0.1)
    
    with st.spinner("Loading rules..."):
        rules_data = fetch_data("rules")
        
    if rules_data and "rules" in rules_data:
        rules = rules_data["rules"]
        
        # Apply local filtering
        filtered_rules = [
            r for r in rules 
            if r['support'] >= min_support 
            and r['confidence'] >= min_confidence 
            and r['lift'] >= min_lift
        ]
        
        st.write(f"Displaying {len(filtered_rules)} rules matching criteria.")
        
        if filtered_rules:
            # Convert to dataframe for nice display
            display_data = []
            for r in filtered_rules:
                display_data.append({
                    "Antecedent": ", ".join(r['antecedents']),
                    "Consequent": ", ".join(r['consequents']),
                    "Support": f"{r['support']:.1%}",
                    "Confidence": f"{r['confidence']:.1%}",
                    "Lift": round(r['lift'], 2)
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No rules match the current filters.")
    else:
        st.warning("Failed to load rules.")

elif page == "Analytics":
    st.header("Analytics")
    
    with st.spinner("Loading rules data for visualizations..."):
        rules_data = fetch_data("rules")
        
    if rules_data and "rules" in rules_data and rules_data["rules"]:
        rules = rules_data["rules"]
        df = pd.DataFrame(rules)
        
        # Simplify lists to strings for plotting
        df['antecedent_str'] = df['antecedents'].apply(lambda x: ", ".join(x))
        df['consequent_str'] = df['consequents'].apply(lambda x: ", ".join(x))
        df['rule_name'] = df['antecedent_str'] + " → " + df['consequent_str']
        
        tab1, tab2, tab3 = st.tabs(["Support vs Confidence", "Top Rules by Lift", "Network Graph"])
        
        with tab1:
            fig = px.scatter(
                df, 
                x="support", 
                y="confidence", 
                size="lift",
                color="lift",
                hover_name="rule_name",
                title="Support vs Confidence (Size & Color = Lift)",
                labels={"support": "Support", "confidence": "Confidence"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            top_lift = df.sort_values("lift", ascending=False).head(15)
            fig = px.bar(
                top_lift,
                x="lift",
                y="rule_name",
                orientation="h",
                title="Top 15 Association Rules by Lift",
                labels={"rule_name": "Rule", "lift": "Lift"}
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            st.write("### Rule Network")
            st.write("A simplified network of the top 20 strongest rules (by confidence).")
            
            # Simple network visualization using plotly
            top_conf = df.sort_values("confidence", ascending=False).head(20)
            
            # Create nodes and edges
            nodes = set()
            edges = []
            
            for _, row in top_conf.iterrows():
                for ant in row['antecedents']:
                    nodes.add(ant)
                    for con in row['consequents']:
                        nodes.add(con)
                        edges.append((ant, con, row['confidence']))
            
            # This is a very simplified visual representation
            # For a true force-directed graph, networkx + plotly or pyvis is better
            st.info("Network visualization would show nodes representing products and directed edges representing associations. Edge thickness = confidence.")
            st.dataframe(top_conf[['rule_name', 'confidence', 'lift']])

elif page == "Algorithm Comparison":
    st.header("Algorithm Comparison")
    
    st.markdown("""
    ### Apriori vs FP-Growth
    
    This project generates frequent itemsets using two algorithms. Here is a theoretical comparison of their performance on large datasets.
    
    | Metric | Apriori | FP-Growth |
    |---|---|---|
    | **Strategy** | Generate-and-test | Divide-and-conquer (FP-Tree) |
    | **Dataset Scans** | Multiple (one per length of itemset) | Only 2 scans |
    | **Memory Usage** | High (candidate generation) | Low (compact tree structure) |
    | **Speed** | Slow on large datasets | Much faster on large datasets |
    | **Output** | Exact same frequent itemsets | Exact same frequent itemsets |
    
    In our training pipeline (see `notebooks/01_EDA_and_Training.ipynb`), **FP-Growth** is utilized to efficiently mine the transactions and extract the patterns in a fraction of the time Apriori would take on a large E-Commerce dataset.
    """)
