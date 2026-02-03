import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Routes 2 Revenue - Brand Intelligence", page_icon="🚀", layout="wide")

# Header
st.title("🚀 Routes 2 Revenue - AI Brand Intelligence")
st.markdown("**Phase 1:** Analyze TikTok Shop brands and identify segments + pain points")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 How It Works")
    st.markdown("""
    **Stage 1: Brand Analysis**

    1. Upload Kalodata export (.xlsx)
    2. AI calculates traffic segments
    3. Assigns pain points per segment
    4. Generates Instantly custom variables
    5. Download Brand Intelligence Sheet

    **3 Segments:**
    - 🏢 HIGH_MALL (50%+ mall)
    - 👤 HIGH_SELF_OP (70%+ self-op)
    - 📈 LOW_AFFILIATE (<10% affiliate)
    - 🔀 MIXED (everything else)
    """)

# Main content
uploaded_file = st.file_uploader("📤 Upload Kalodata Export", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Read the file
        df = pd.read_excel(uploaded_file)

        st.success(f"✅ Loaded {len(df)} brands from Kalodata")

        # Calculate traffic percentages
        df['Self_Op_Percent'] = (df['Self-Operated Account Revenue(£)'] / df['Revenue(£)'] * 100).round(1)
        df['Affiliate_Percent'] = (df['Affiliate Revenue(£)'] / df['Revenue(£)'] * 100).round(1)
        df['Mall_Percent'] = (df['Shopping Mall Revenue(£)'] / df['Revenue(£)'] * 100).round(1)

        # Calculate segments
        def calculate_segment(row):
            self_op = row['Self_Op_Percent']
            affiliate = row['Affiliate_Percent']
            mall = row['Mall_Percent']

            if mall >= 50:
                return 'HIGH_MALL'
            if self_op >= 70:
                return 'HIGH_SELF_OP'
            if affiliate < 10:
                return 'LOW_AFFILIATE'
            return 'MIXED'

        df['Segment'] = df.apply(calculate_segment, axis=1)

        # Assign pain points
        pain_map = {
            'HIGH_MALL': 'Platform Risk',
            'HIGH_SELF_OP': 'Time Prison',
            'LOW_AFFILIATE': 'Revenue Left on Table',
            'MIXED': 'Growth Opportunity'
        }
        df['Primary_Pain_Point'] = df['Segment'].map(pain_map)

        # Generate custom variables
        def generate_custom_vars(row):
            segment = row['Segment']
            self_op = row['Self_Op_Percent']
            affiliate = row['Affiliate_Percent']
            mall = row['Mall_Percent']

            if segment == 'HIGH_MALL':
                c1 = f"{mall:.0f}% of your traffic is rented from TikTok Mall"
                c2 = "mall dependency"
                c3 = "platform risk is real - one algo change could impact revenue"
            elif segment == 'HIGH_SELF_OP':
                c1 = f"{self_op:.0f}% of traffic through your own content"
                c2 = "running everything yourself"
                c3 = "scaling without burning yourself out"
            elif segment == 'LOW_AFFILIATE':
                c1 = f"only {affiliate:.0f}% affiliate traffic"
                c2 = f"{100-affiliate:.0f}% of revenue channels untapped"
                c3 = "competitors are outpacing you on affiliates"
            else:
                max_channel = max(self_op, affiliate, mall)
                if max_channel == self_op:
                    c1 = f"{self_op:.0f}% self-operated but room to scale with affiliates"
                elif max_channel == mall:
                    c1 = f"{mall:.0f}% mall traffic with room to diversify"
                else:
                    c1 = f"{affiliate:.0f}% affiliate but could diversify further"
                c2 = "balanced traffic mix"
                c3 = "opportunity to optimize your channel strategy"

            return pd.Series([c1, c2, c3])

        df[['Custom1', 'Custom2', 'Custom3']] = df.apply(generate_custom_vars, axis=1)

        # Priority tier
        df['Priority_Tier'] = df['Revenue(£)'].apply(lambda x: 'A' if x >= 9500 else ('B' if x >= 8000 else 'C'))

        # Create Brand Intelligence Sheet
        brand_intelligence = df[[
            'Shop Name', 'Revenue(£)', 'Avg. Unit Price(£)',
            'Self_Op_Percent', 'Affiliate_Percent', 'Mall_Percent',
            'Segment', 'Primary_Pain_Point', 'Priority_Tier',
            'Custom1', 'Custom2', 'Custom3', 'KalodataUrl'
        ]].copy()

        brand_intelligence.columns = [
            'Brand_Name', 'Monthly_Revenue_GBP', 'Avg_Unit_Price_GBP',
            'Self_Op_Percent', 'Affiliate_Percent', 'Mall_Percent',
            'Segment', 'Primary_Pain_Point', 'Priority_Tier',
            'Custom_Var_1', 'Custom_Var_2', 'Custom_Var_3', 'Brand_URL'
        ]

        brand_intelligence = brand_intelligence.sort_values(
            ['Priority_Tier', 'Monthly_Revenue_GBP'], 
            ascending=[True, False]
        )

        # Display metrics
        st.markdown("---")
        st.header("📊 Segment Breakdown")

        col1, col2, col3, col4 = st.columns(4)

        segment_counts = brand_intelligence['Segment'].value_counts()

        with col1:
            st.metric("🏢 HIGH_MALL", segment_counts.get('HIGH_MALL', 0))
            st.caption("50%+ mall traffic")
        with col2:
            st.metric("👤 HIGH_SELF_OP", segment_counts.get('HIGH_SELF_OP', 0))
            st.caption("70%+ self-operated")
        with col3:
            st.metric("📈 LOW_AFFILIATE", segment_counts.get('LOW_AFFILIATE', 0))
            st.caption("<10% affiliate")
        with col4:
            st.metric("🔀 MIXED", segment_counts.get('MIXED', 0))
            st.caption("Mixed traffic")

        # Pie chart
        st.markdown("---")
        fig = px.pie(
            segment_counts.reset_index(), 
            values='count', 
            names='Segment',
            title='Segment Distribution',
            color_discrete_map={
                'HIGH_MALL': '#ef4444',
                'HIGH_SELF_OP': '#3b82f6',
                'LOW_AFFILIATE': '#f59e0b',
                'MIXED': '#6b7280'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show examples by segment
        st.markdown("---")
        st.header("🎯 Example Brands by Segment")

        segments = ['HIGH_MALL', 'HIGH_SELF_OP', 'LOW_AFFILIATE', 'MIXED']

        for seg in segments:
            seg_brands = brand_intelligence[brand_intelligence['Segment'] == seg].head(3)
            if len(seg_brands) > 0:
                with st.expander(f"**{seg}** ({len(brand_intelligence[brand_intelligence['Segment'] == seg])} brands)"):
                    for idx, row in seg_brands.iterrows():
                        st.markdown(f"""
                        **{row['Brand_Name']}**  
                        💰 Revenue: £{row['Monthly_Revenue_GBP']:,.2f} | 🏷️ Avg Price: £{row['Avg_Unit_Price_GBP']:.2f}  
                        📊 Traffic: {row['Self_Op_Percent']:.0f}% self / {row['Affiliate_Percent']:.0f}% aff / {row['Mall_Percent']:.0f}% mall  
                        🎯 Pain Point: {row['Primary_Pain_Point']}  
                        📧 Email Hook: *"{row['Custom_Var_1']}"*
                        """)
                        st.markdown("---")

        # Full data table
        st.markdown("---")
        st.header("📋 Full Brand Intelligence Sheet")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            segment_filter = st.multiselect(
                "Filter by Segment",
                options=['ALL'] + list(brand_intelligence['Segment'].unique()),
                default=['ALL']
            )
        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=['ALL', 'A', 'B', 'C'],
                default=['ALL']
            )

        # Apply filters
        filtered_df = brand_intelligence.copy()
        if 'ALL' not in segment_filter:
            filtered_df = filtered_df[filtered_df['Segment'].isin(segment_filter)]
        if 'ALL' not in priority_filter:
            filtered_df = filtered_df[filtered_df['Priority_Tier'].isin(priority_filter)]

        st.dataframe(filtered_df, use_container_width=True, height=400)

        # Download button
        st.markdown("---")
        st.header("📥 Export")

        csv = brand_intelligence.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Brand Intelligence Sheet (CSV)",
            data=csv,
            file_name="Brand_Intelligence_Sheet.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.success("✅ Ready for Stage 2: Manual lead research in Apollo/Lusha")

        with st.expander("📝 Next Steps"):
            st.markdown("""
            **What to do with this data:**

            1. **Download the CSV** above
            2. **Review Priority A brands** (highest revenue)
            3. **Search Apollo/Lusha** for contacts at each brand
            4. **Target these roles:**
               - Tier 1: Founder, Co-Founder, CEO, Owner, Managing Director
               - Tier 2: Head of Marketing, Marketing Director, Head of Growth
               - Tier 3: Ecommerce Director, Ops Director, Social Media Manager
            5. **Create Lead Research Sheet** with contacts you find
            6. **Come back for Stage 3:** Upload your contacts for pain point matching

            **You'll get:**
            - Each contact matched to the right pain point for their role
            - Custom variables ready for your 6-step Instantly sequence
            - Split by segment for 4 separate campaigns
            """)

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Make sure you're uploading a Kalodata export with the correct column format.")

else:
    # Landing state
    st.info("👆 Upload a Kalodata export to get started")

    st.markdown("---")
    st.header("📋 What You'll Get")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🎯 Segment Analysis**
        - HIGH_MALL brands
        - HIGH_SELF_OP brands
        - LOW_AFFILIATE brands
        - MIXED brands
        """)

    with col2:
        st.markdown("""
        **💡 Pain Points**
        - Platform Risk
        - Time Prison
        - Revenue Left on Table
        - Growth Opportunity
        """)

    with col3:
        st.markdown("""
        **📧 Email Hooks**
        - Custom variables for Instantly
        - Data-backed hooks
        - Ready for 6-step sequence
        """)

# Footer
st.markdown("---")
st.caption("Routes 2 Revenue - Phase 1: Brand Intelligence Engine v1.0")
