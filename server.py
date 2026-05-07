import os
from fastmcp import FastMCP
from google.ads.googleads.client import GoogleAdsClient

mcp = FastMCP("Google Ads MCP")

def get_client():
    credentials = {
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"],
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(credentials)

@mcp.tool()
def get_campaigns(customer_id: str = None) -> str:
    """Lista todas as campanhas da conta Google Ads com performance."""
    client = get_client()
    cid = customer_id or os.environ["GOOGLE_ADS_CUSTOMER_ID"]
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.ctr
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    response = ga_service.search(customer_id=cid, query=query)
    results = []
    for row in response:
        results.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name,
            "cost": round(row.metrics.cost_micros / 1_000_000, 2),
            "clicks": row.metrics.clicks,
            "impressions": row.metrics.impressions,
            "conversions": row.metrics.conversions,
            "ctr": round(row.metrics.ctr * 100, 2),
        })
    return str(results)

@mcp.tool()
def get_keywords(customer_id: str = None) -> str:
    """Lista palavras-chave com performance dos últimos 30 dias."""
    client = get_client()
    cid = customer_id or os.environ["GOOGLE_ADS_CUSTOMER_ID"]
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.ctr
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
    """
    response = ga_service.search(customer_id=cid, query=query)
    results = []
    for row in response:
        results.append({
            "keyword": row.ad_group_criterion.keyword.text,
            "match_type": row.ad_group_criterion.keyword.match_type.name,
            "cost": round(row.metrics.cost_micros / 1_000_000, 2),
            "clicks": row.metrics.clicks,
            "impressions": row.metrics.impressions,
            "conversions": row.metrics.conversions,
            "ctr": round(row.metrics.ctr * 100, 2),
        })
    return str(results)

@mcp.tool()
def get_search_terms(customer_id: str = None) -> str:
    """Lista termos de pesquisa que ativaram seus anúncios."""
    client = get_client()
    cid = customer_id or os.environ["GOOGLE_ADS_CUSTOMER_ID"]
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            search_term_view.search_term,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 50
    """
    response = ga_service.search(customer_id=cid, query=query)
    results = []
    for row in response:
        results.append({
            "search_term": row.search_term_view.search_term,
            "cost": round(row.metrics.cost_micros / 1_000_000, 2),
            "clicks": row.metrics.clicks,
            "impressions": row.metrics.impressions,
            "conversions": row.metrics.conversions,
        })
    return str(results)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
