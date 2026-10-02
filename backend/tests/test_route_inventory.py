"""Fail when a new business endpoint is added without explicit test inventory."""
import pytest


EXPECTED_ROUTES = {
    ('GET', '/'),
    ('GET', '/test-db'),
    ('GET', '/api/auth/config'),
    ('POST', '/api/auth/login'),
    ('POST', '/api/auth/google'),
    ('POST', '/api/auth/register'),
    ('POST', '/api/auth/forgot-password'),
    ('POST', '/api/auth/verify-otp'),
    ('POST', '/api/auth/reset-password'),
    ('GET', '/api/auth/me'),
    ('PUT', '/api/auth/change-password'),
    ('GET', '/api/stocks'),
    ('GET', '/api/stock-data/<symbol>'),
    ('POST', '/api/fetch-stock'),
    ('GET', '/api/news/<symbol>'),
    ('GET', '/api/predict/<symbol>'),
    ('GET', '/api/analysis/<symbol>'),
    ('POST', '/api/backtest/<symbol>'),
    ('GET', '/api/copilot/history'),
    ('DELETE', '/api/copilot/history'),
    ('POST', '/api/copilot/chat'),
    ('POST', '/api/admin/stocks'),
    ('DELETE', '/api/admin/stocks/<symbol>'),
    ('POST', '/api/admin/run-scraper'),
    ('POST', '/api/admin/train-models'),
    ('POST', '/api/admin/train-models/sync'),
    ('GET', '/api/admin/users'),
    ('PUT', '/api/admin/users/<int:user_id>'),
    ('DELETE', '/api/admin/users/<int:user_id>'),
    ('GET', '/api/admin/logs'),
}


@pytest.mark.case('API-17', 'Route Inventory ครอบคลุม Business API ทุก Endpoint',
                  'เมื่อเพิ่ม route ใหม่ test นี้จะ fail จนกว่าจะเพิ่ม test case รองรับ')
def test_api_17_all_business_routes_are_in_test_inventory(app):
    actual = set()
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        for method in rule.methods - {'HEAD', 'OPTIONS'}:
            actual.add((method, str(rule)))

    assert actual == EXPECTED_ROUTES
