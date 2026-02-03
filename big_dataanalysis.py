"""
Big Data Analysis with PySpark
CodeTech Internship Project
Author: [Your Name]
Date: February 2026

This script demonstrates scalable big data processing using Apache Spark
to analyze large datasets with distributed computing capabilities.
"""

# Install PySpark if not already installed
# !pip install pyspark matplotlib pandas

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg, max, min, sum, count, stddev, 
    percentile_approx, col, when, desc
)
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import matplotlib.pyplot as plt
import pandas as pd
import time

# ============================================================================
# SECTION 1: SPARK SESSION INITIALIZATION
# ============================================================================

print("=" * 80)
print("BIG DATA ANALYSIS WITH PYSPARK")
print("=" * 80)

# Create Spark Session with optimized configuration
spark = SparkSession.builder \
    .appName("BigDataAnalysis_CodeTech") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

print(f"\n✓ Spark Session Created")
print(f"  - Application Name: {spark.sparkContext.appName}")
print(f"  - Spark Version: {spark.version}")
print(f"  - Master: {spark.sparkContext.master}")

# ============================================================================
# SECTION 2: DATA GENERATION (Simulating Large Dataset)
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING LARGE DATASET")
print("=" * 80)

# Generate a larger dataset (1 million records for demonstration)
start_time = time.time()

# Creating synthetic e-commerce sales data
data = [
    (
        i,
        f"Category_{i % 5}",  # 5 categories
        i * 10,
        f"Region_{i % 10}",   # 10 regions
        i % 100,              # Customer ID
        (i * 7) % 1000        # Discount amount
    )
    for i in range(1, 1000001)  # 1 million records
]

columns = ["id", "category", "value", "region", "customer_id", "discount"]

df = spark.createDataFrame(data, columns)

# Cache the dataframe for better performance
df.cache()

generation_time = time.time() - start_time
print(f"\n✓ Dataset Generated in {generation_time:.2f} seconds")
print(f"  - Total Records: {df.count():,}")
print(f"  - Number of Columns: {len(df.columns)}")

# ============================================================================
# SECTION 3: DATA EXPLORATION
# ============================================================================

print("\n" + "=" * 80)
print("DATA EXPLORATION")
print("=" * 80)

print("\n--- Sample Data (First 10 rows) ---")
df.show(10)

print("\n--- Schema Information ---")
df.printSchema()

print("\n--- Basic Statistics ---")
df.describe().show()

# ============================================================================
# SECTION 4: DATA QUALITY CHECKS
# ============================================================================

print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)

# Check for null values
print("\n--- Null Value Check ---")
from pyspark.sql.functions import isnull
null_counts = df.select([count(when(isnull(c), c)).alias(c) for c in df.columns])
null_counts.show()

# Check for duplicates
duplicate_count = df.count() - df.dropDuplicates().count()
print(f"\n✓ Duplicate Records: {duplicate_count:,}")

# Data cleaning
df_clean = df.dropna()
print(f"✓ Records after removing nulls: {df_clean.count():,}")

# ============================================================================
# SECTION 5: ADVANCED ANALYTICS
# ============================================================================

print("\n" + "=" * 80)
print("ADVANCED ANALYTICS")
print("=" * 80)

# Analysis 1: Category-wise Analysis
print("\n--- Analysis 1: Category Performance ---")
category_analysis = df_clean.groupBy("category").agg(
    count("id").alias("Total_Transactions"),
    avg("value").alias("Average_Value"),
    max("value").alias("Max_Value"),
    min("value").alias("Min_Value"),
    sum("value").alias("Total_Revenue"),
    stddev("value").alias("Std_Deviation")
).orderBy(desc("Total_Revenue"))

category_analysis.show()

# Analysis 2: Regional Analysis
print("\n--- Analysis 2: Regional Performance ---")
regional_analysis = df_clean.groupBy("region").agg(
    count("id").alias("Total_Sales"),
    avg("value").alias("Avg_Sale_Value"),
    sum("discount").alias("Total_Discounts"),
    (sum("value") - sum("discount")).alias("Net_Revenue")
).orderBy(desc("Net_Revenue"))

regional_analysis.show(10)

# Analysis 3: Customer Behavior Analysis
print("\n--- Analysis 3: Top 10 Customers by Total Spending ---")
customer_analysis = df_clean.groupBy("customer_id").agg(
    count("id").alias("Purchase_Count"),
    sum("value").alias("Total_Spent"),
    avg("value").alias("Avg_Purchase_Value"),
    sum("discount").alias("Total_Discounts_Received")
).orderBy(desc("Total_Spent"))

customer_analysis.show(10)

# Analysis 4: Value Distribution Analysis
print("\n--- Analysis 4: Value Distribution Percentiles ---")
percentiles = df_clean.select(
    percentile_approx("value", 0.25).alias("25th_Percentile"),
    percentile_approx("value", 0.50).alias("Median"),
    percentile_approx("value", 0.75).alias("75th_Percentile"),
    percentile_approx("value", 0.90).alias("90th_Percentile"),
    percentile_approx("value", 0.95).alias("95th_Percentile")
)
percentiles.show()

# Analysis 5: Filtering and Complex Queries
print("\n--- Analysis 5: High-Value Transactions (Value > 500,000) ---")
high_value_df = df_clean.filter(col('value') > 500000)
print(f"High-value transactions: {high_value_df.count():,}")
high_value_df.show(10)

# Analysis 6: Category and Region Cross-Analysis
print("\n--- Analysis 6: Category-Region Performance Matrix ---")
cross_analysis = df_clean.groupBy("category", "region").agg(
    count("id").alias("Transaction_Count"),
    avg("value").alias("Avg_Value")
).orderBy("category", desc("Avg_Value"))

cross_analysis.show(20)

# ============================================================================
# SECTION 6: PERFORMANCE METRICS
# ============================================================================

print("\n" + "=" * 80)
print("PERFORMANCE METRICS")
print("=" * 80)

# Measure query performance
print("\n--- Query Performance Test ---")

# Test 1: Simple aggregation
start = time.time()
result1 = df_clean.groupBy("category").count().collect()
time1 = time.time() - start
print(f"Simple Aggregation: {time1:.4f} seconds")

# Test 2: Complex aggregation
start = time.time()
result2 = df_clean.groupBy("category", "region").agg(
    avg("value"), max("value"), min("value")
).collect()
time2 = time.time() - start
print(f"Complex Aggregation: {time2:.4f} seconds")

# Test 3: Filtering and sorting
start = time.time()
result3 = df_clean.filter(col("value") > 500000).orderBy(desc("value")).take(100)
time3 = time.time() - start
print(f"Filter and Sort: {time3:.4f} seconds")

# ============================================================================
# SECTION 7: VISUALIZATION
# ============================================================================

print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# Convert to Pandas for visualization
pandas_category = category_analysis.toPandas()
pandas_regional = regional_analysis.toPandas()

# Visualization 1: Category Distribution (Donut Chart)
plt.figure(figsize=(10, 8))
plt.subplot(2, 2, 1)
plt.pie(
    pandas_category['Total_Transactions'],
    labels=pandas_category['category'],
    autopct='%1.1f%%',
    startangle=90,
    colors=['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0']
)
centre_circle = plt.Circle((0, 0), 0.6, fc='white')
plt.gca().add_artist(centre_circle)
plt.title("Category Distribution (Transaction Count)", fontsize=12, fontweight='bold')

# Visualization 2: Revenue by Category (Bar Chart)
plt.subplot(2, 2, 2)
plt.bar(pandas_category['category'], pandas_category['Total_Revenue'], 
        color='#2196F3', alpha=0.7)
plt.xlabel('Category', fontweight='bold')
plt.ylabel('Total Revenue', fontweight='bold')
plt.title('Revenue by Category', fontsize=12, fontweight='bold')
plt.xticks(rotation=45)

# Visualization 3: Regional Performance (Horizontal Bar Chart)
plt.subplot(2, 2, 3)
top_regions = pandas_regional.head(10)
plt.barh(top_regions['region'], top_regions['Net_Revenue'], color='#4CAF50', alpha=0.7)
plt.xlabel('Net Revenue', fontweight='bold')
plt.ylabel('Region', fontweight='bold')
plt.title('Top 10 Regions by Net Revenue', fontsize=12, fontweight='bold')

# Visualization 4: Average Value by Category (Line Plot)
plt.subplot(2, 2, 4)
plt.plot(pandas_category['category'], pandas_category['Average_Value'], 
         marker='o', linewidth=2, markersize=8, color='#E91E63')
plt.xlabel('Category', fontweight='bold')
plt.ylabel('Average Value', fontweight='bold')
plt.title('Average Transaction Value by Category', fontsize=12, fontweight='bold')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/big_data_visualizations.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualizations saved to 'big_data_visualizations.png'")

# ============================================================================
# SECTION 8: KEY INSIGHTS SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("KEY INSIGHTS SUMMARY")
print("=" * 80)

total_revenue = df_clean.agg(sum("value")).collect()[0][0]
avg_transaction = df_clean.agg(avg("value")).collect()[0][0]
total_customers = df_clean.select("customer_id").distinct().count()

print(f"""
BUSINESS METRICS:
-----------------
• Total Transactions: {df_clean.count():,}
• Total Revenue: ${total_revenue:,.2f}
• Average Transaction Value: ${avg_transaction:,.2f}
• Unique Customers: {total_customers:,}
• High-Value Transactions (>$500K): {high_value_df.count():,}

TOP PERFORMING CATEGORY:
------------------------
• {pandas_category.iloc[0]['category']}: ${pandas_category.iloc[0]['Total_Revenue']:,.2f}

TOP PERFORMING REGION:
----------------------
• {pandas_regional.iloc[0]['region']}: ${pandas_regional.iloc[0]['Net_Revenue']:,.2f}

SCALABILITY DEMONSTRATION:
--------------------------
• Dataset Size: 1 Million Records
• Processing Time: {generation_time:.2f} seconds
• Distributed Computing: Enabled
• Adaptive Query Execution: Active
""")

# ============================================================================
# SECTION 9: CLEANUP
# ============================================================================

print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)

# Unpersist cached data
df.unpersist()

print("\n✓ Analysis Complete!")
print("✓ All results have been generated successfully")
print("✓ Visualizations saved")

# Keep Spark session open for notebook usage
# Uncomment the following line to stop the session in scripts
# spark.stop()
