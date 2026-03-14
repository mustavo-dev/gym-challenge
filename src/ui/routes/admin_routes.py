"""Admin-facing UI routes."""

from flask import Blueprint, render_template

admin_bp = Blueprint(
    "admin",
    __name__,
)

@admin_bp.get("/admin")
def admin_dashboard():
    """Render the admin dashboard."""
    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard",
    )
