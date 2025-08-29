# Create a high-level architecture diagram using matplotlib (no external dependencies).
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

# Figure setup
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def box(x, y, w, h, label):
    rect = Rectangle((x, y), w, h, fill=False)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=9, wrap=True)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrow(x1, y1, x2-x1, y2-y1, width=0.2, length_includes_head=True, head_width=2.5, head_length=2.5))

# Layout coordinates
W, H = 18, 10  # width and height for boxes
gap_x = 3
gap_y = 6

# Row 1 (Top): Orchestrator, CI/CD & IaC, Observability, Secrets
box(5, 86, W, H, "Orchestrator\n(Airflow / Prefect)")
box(41, 86, W, H, "CI/CD & IaC\n(GitHub Actions, Terraform)")
box(77, 86, W, H, "Observability\n(Logs, Metrics, Tracing)")

# Row 2: Product Discovery -> Data Lake/Warehouse -> Scoring
box(5, 66, W, H, "Product Discovery\n(Scrapers/API: Amazon, eBay,\nAliExpress, Google Trends,\nTikTok, Instagram)")
box(41, 66, W, H, "Storage Layer\n(PostgreSQL + S3/Parquet)")
box(77, 66, W, H, "Scoring & Selection\n(Python + dbt models)")

arrow(23+gap_x, 71, 41, 71)   # Discovery -> Storage
arrow(59+gap_x, 71, 77, 71)   # Storage -> Scoring

# Row 3: Content Generation -> Catalog Publisher -> Storefront & Funnels
box(5, 46, W, H, "Content Generation\n(LLM: descrieri; Image: gen/optimizare;\nKeywording SEO)")
box(41, 46, W, H, "Catalog Publisher\n(API Shopify / WooCommerce)")
box(77, 46, W, H, "Storefront & Funnels\n(Shopify/Woo + LPs, A/B)")

arrow(23+gap_x, 51, 41, 51)   # Content -> Publisher
arrow(59+gap_x, 51, 77, 51)   # Publisher -> Storefront

# Row 4: Ads, CRM, Orders/ERP, Payments
box(5, 26, W, H, "Ads Automation\n(Meta Ads API, TikTok Ads API,\nGoogle Ads API)")
box(41, 26, W, H, "CRM & Email\n(Klaviyo/Mailchimp)\n(Abandon cart, upsell)")
box(77, 26, W, H, "Orders & Fulfillment\n(Dropshipping API/Odoo)\n(Tracking, Returns)")

arrow(77, 46, 88, 36)  # Storefront -> Orders
arrow(77, 46, 50, 36)  # Storefront -> CRM
arrow(77, 46, 15, 36)  # Storefront -> Ads

# Row 5: Payments & Analytics
box(5, 6, W, H, "Payments\n(Stripe/PayPal)")
box(41, 6, W, H, "Analytics\n(GA4, Pixels, Metabase)")

arrow(86, 26, 86, 16)  # Orders -> Payments
arrow(86, 46, 50, 16)  # Storefront -> Analytics
arrow(15, 26, 50, 16)  # Ads -> Analytics
arrow(50, 26, 50, 16)  # CRM -> Analytics
arrow(50, 66, 50, 16)  # Storage -> Analytics

# Orchestrator arrows
arrow(14, 86, 14, 76)  # Orchestrator -> Discovery
arrow(50, 86, 50, 76)  # Orchestrator -> Storage
arrow(86, 86, 86, 76)  # Orchestrator -> Scoring
arrow(14, 86, 14, 56)  # Orchestrator -> Content
arrow(50, 86, 50, 56)  # Orchestrator -> Publisher
arrow(86, 86, 86, 56)  # Orchestrator -> Storefront
arrow(14, 86, 14, 36)  # Orchestrator -> Ads
arrow(50, 86, 50, 36)  # Orchestrator -> CRM
arrow(86, 86, 86, 36)  # Orchestrator -> Orders

# Observability arrows (from multiple components)
for (x, y) in [(14,71),(50,71),(86,71),(14,51),(50,51),(86,51),(14,31),(50,31),(86,31),(14,11),(50,11)]:
    arrow(86, 86, x, y)  # Observability receives from components

# Save the diagram
out_path = "/mnt/data/arch_ecommerce_automation.png"
plt.savefig(out_path, bbox_inches='tight', dpi=200)
out_path
