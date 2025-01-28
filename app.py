import streamlit as st
import pandas as pd
import plotly.express as px

# Title for the Streamlit app
st.title("Top Global Cities for Financial Independence")

# Instructions for Using the Tool
st.write("### Instructions for Using the Tool")

instructions = """
- This tool helps identify the most suitable **cities** for pursuing FI during the accumulation phase.
- Select your **current country** from the dropdown menu above the graph. You can choose multiple countries if you wish.
- Select your **reference city**: The graph maps **percentage differences** in salaries and cost of living (COL) relative to your selected city.
- The **red dashed line** serves as a benchmark:
  - Cities **above the red line** may provide better opportunities for pursuing financial independence.
  - Cities **on the red line** have equivalent percentage differences in both salaries and COL (e.g., a 10% higher salary but also a 10% higher COL).
  - Cities **below the red line** may provide worse opportunities for pursuing financial independence.
- Hover over the top right of the figure and use the zoom tool (draw a square on the figure), zoom in/out, pan, and other functions to better visualize your cities of interest.
- Example: With Los Angeles, CA as the reference, we observe that Seatle has a **39.4% higher average salary**, while its **cost of living is 1.6% lower**. Pursuing FI in Seatle is likely to be easier, on average, than in LA.
- Data on salaries and cost of living is from **Numbeo (2024)**.
"""

st.write(instructions)

# Load the embedded Excel file automatically
@st.cache_data
def load_data():
    file_path = "Col_Sal_Cities_Global.xlsx"  # Ensure this file is in the same directory
    data = pd.read_excel(file_path, sheet_name="City_global")

    # Clean and format the City column
    data = data.dropna(subset=['City', 'Salary', 'COL 2024'])  # Drop rows where 'City', 'Salary' or 'COL 2024' is NaN
    data['City'] = data['City'].astype(str).str.strip().str.title()  # Convert to string and clean text

    # Extract country name from the city column
    data['Country'] = data['City'].apply(lambda x: x.split(',')[-1].strip())
    
    # Extract short city names for display
    data['City_Short'] = data['City'].apply(lambda x: x.split(',')[0])

    return data

data = load_data()

# Create dropdown for country selection (multi-select)
st.write("### Select Countries to Display Cities From")
selected_countries = st.multiselect("Choose Countries:", sorted(data['Country'].unique()))

# Filter cities based on selected countries
filtered_data = data[data['Country'].isin(selected_countries)]

# Ensure there are available cities to choose from
if not filtered_data.empty:
    # Create a dropdown for selecting the reference city
    st.write("### Select Reference City")
    city_options = sorted(filtered_data['City'].unique())
    reference_city = st.selectbox("Select Reference City:", options=city_options)
    
    # Function to calculate percentage differences
    def calculate_differences(data, reference_city):
        ref_data = data[data['City'] == reference_city].iloc[0]
        data['Sal_Diff_%'] = ((data['Salary'] - ref_data['Salary']) / ref_data['Salary']) * 100
        data['Col_Diff_%'] = ((data['COL 2024'] - ref_data['COL 2024']) / ref_data['COL 2024']) * 100
        return data

    filtered_data = calculate_differences(filtered_data, reference_city)
    
    # Function to create scatter plot
    def create_scatter_plot(data, reference_city):
        fig = px.scatter(
            data,
            x='Col_Diff_%',
            y='Sal_Diff_%',
            text='City_Short',
            color='Country',  # Assign colors by country
            hover_data={'City': True, 'Col_Diff_%': ':.1f', 'Sal_Diff_%': ':.1f'},
            labels={
                'Col_Diff_%': 'Cost of Living Difference (%)',
                'Sal_Diff_%': 'Salary Difference (%)',
            },
            title=f"Cost of Living vs Salary Comparison (Reference: {reference_city})",
            template="plotly_dark",
        )
        
        # Add red benchmark line
        fig.add_shape(
            type="line", x0=-1000, x1=1000, y0=-1000, y1=1000,
            line=dict(color="red", dash="dash", width=2),
        )
        
        # Customize markers and layout
        fig.update_traces(marker=dict(size=13, line=dict(width=2, color='DarkSlateGrey')),
                          textposition='top center')
        
        # Adjust axis limits based on actual data range
        x_min, x_max = data['Col_Diff_%'].min(), data['Col_Diff_%'].max()
        y_min, y_max = data['Sal_Diff_%'].min(), data['Sal_Diff_%'].max()
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        
        fig.update_xaxes(range=[x_min - x_margin, x_max + x_margin],
                         showgrid=True, gridcolor="rgba(200,200,200,0.2)", gridwidth=1, 
                         zeroline=True, zerolinecolor='rgba(180,180,180,0.5)', zerolinewidth=2, 
                         showline=False)
        
        fig.update_yaxes(range=[y_min - y_margin, y_max + y_margin],
                         showgrid=True, gridcolor="rgba(200,200,200,0.2)", gridwidth=1, 
                         zeroline=True, zerolinecolor='rgba(180,180,180,0.5)', zerolinewidth=2, 
                         showline=False)
        
        fig.update_layout(
            height=600, width=1200,
            paper_bgcolor='black', plot_bgcolor='black',
            margin=dict(l=40, r=40, t=50, b=5),
            legend=dict(title_text="Selected Countries", font=dict(color="white")),  # Make legend text white
            title=dict(
                text=f"Cost of Living vs Salary Comparison (Reference: {reference_city})",
                font=dict(size=18, color="white"),  # Make title more visible
            ),
            showlegend=True
        )
        
        return fig

    # Display the plot
    scatter_plot = create_scatter_plot(filtered_data, reference_city)
    st.plotly_chart(scatter_plot, use_container_width=True)
else:
    st.write("⚠ Please select at least one country to proceed.")


