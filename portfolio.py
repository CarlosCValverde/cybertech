from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import jsonify

from auth import login_required
from models import get_db
import models
from utils import objects_to_dict

bp = Blueprint("portfolio", __name__)


@bp.route("/")
@login_required
def index():

    return render_template("portfolio/index.html")


@bp.route("/portfolio/search")
@login_required
def search():

    q = request.args.get("q")
    db = get_db()
    if q:
        projects = db.query(models.Project).join(models.User).filter(models.User.id == session["user_id"], models.Project.address.like(f"%{q}%")).all()
        projects = [objects_to_dict(project) for project in projects]
    else:
        projects = []
    return jsonify(projects)



@bp.route("/portfolio/projects")
@login_required
def projects():
    """Show all the projects, most recent first."""
    db = get_db()

    projects = db.query(models.Project.p_type, models.Project.po_number, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.start_date, models.Project.invoice, models.Project.datto).join(models.User, models.Project.user_id == models.User.id).order_by(models.Project.created_at.desc()).all()

    return render_template("portfolio/projects.html", projects=projects)
    


@bp.route("/portfolio/newproject", methods=["GET", "POST"])
@login_required
def newproject():

    if request.method == "POST":

        # Related to Project table
        p_type = request.form.get("p_type")
        po_number = request.form.get("po_number")
        address = request.form.get("address")
        num_chargers = request.form.get("num_chargers")
        permit_num = request.form.get("permit_num")
        project_status = request.form.get("project_status")
        start_date = request.form.get("start_date")
        invoice = request.form.get("invoice")
        datto = request.form.get("datto")

        # Related to Inspection table
        i_type = request.form.get("i_type")
        inspection_status = request.form.get("inspection_status")
        inspection_date = request.form.get("inspection_date")  

        error = None

        if not p_type:
            error = "Project type is required"
        elif not po_number:
            error = "Purchase order number is required"
        elif not address:
            error = "Address is required"
        elif not num_chargers:
            error = "Number of chargers is required"
        elif not project_status:
            error = "Project status is required"
        elif not invoice:
            error = "Invoice is required"
        elif not datto:
            error = "Uploaded to datto is required"
        elif not i_type:
            error = "Inspection type is required"
        elif not inspection_status:
            error = "Inspection status is required"

        if error is None:
            db = get_db()
            new_project = models.Project(
                p_type=p_type,
                po_number=po_number,
                address=address,
                num_chargers=num_chargers,
                permit_num=permit_num,
                project_status=project_status,
                start_date=start_date,
                invoice=invoice,
                datto=datto,
                user_id=session["user_id"]
            )
            db.add(new_project)
            db.commit()
            project_id = new_project.id

            new_inspection = models.Inspection(
                i_type=i_type,
                inspection_status=inspection_status,
                inspection_date=inspection_date,
                project_id=project_id
            )
            db.add(new_inspection)
            db.commit()
            inspection_id=new_inspection.id

            new_compositekey = models.CompositeKey(
                user_id=session["user_id"],
                project_id=project_id,
                inspection_id=inspection_id
            )
            db.add(new_compositekey)
            db.commit()

            flash("Project Saved!")
            return redirect(url_for("portfolio.projects"))
    
        flash(error)

    else:
        project_status = ["active", "completed", "on_hold"]
        i_type = ["underground", "rough", "power_release", "final", "pending"]
        inspection_status = ["passed", "rescheduled", "pending"]
        p_type = ["dwp", "sce"]
        invoice = ["50%", "90%", "100%"]
        datto = ["completed", "partial", "empty"]

        return render_template("portfolio/newproject.html", project_status=project_status, i_type=i_type, inspection_status=inspection_status, p_type=p_type, invoice=invoice, datto=datto)


@bp.route("/portfolio/datto", methods=['GET'])
@login_required
def datto():
    """Filter projects, by uploaded to datto."""
    db = get_db()

    datto = request.args.get("datto")

    projects = db.query(models.Project.p_type, models.Project.po_number, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.start_date, models.Project.invoice, models.Project.datto).join(models.User, models.Project.user_id == models.User.id).filter(models.Project.datto == datto).order_by(models.Project.created_at.desc()).all()

    return render_template("portfolio/datto.html", projects=projects)


@bp.route("/portfolio/utils", methods=["POST"])
@login_required
def utils():
    """Filter projects, by type."""
    db = get_db()

    p_type = request.form.get("dropdown")

    if p_type == "dwp":
        projects = db.query(models.Project.p_type, models.Project.po_number, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.start_date, models.Project.invoice, models.Project.datto).join(models.User, models.Project.user_id == models.User.id).filter(models.Project.p_type == p_type).order_by(models.Project.created_at.desc()).all()

        return render_template("portfolio/utils.html", projects=projects, p_type=p_type)

    elif p_type == "sce":
        projects = db.query(models.Project.p_type, models.Project.po_number, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.start_date, models.Project.invoice, models.Project.datto).join(models.User, models.Project.user_id == models.User.id).filter(models.Project.p_type == p_type).order_by(models.Project.created_at.desc()).all()

        return render_template("portfolio/utils.html", projects=projects, p_type=p_type)
    

@bp.route("/portfolio/summary", methods=['GET'])
@login_required
def summary():
    """Summary"""
    db = get_db()

    projects = db.query(models.Project.p_type, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.datto, models.Inspection.i_type, models.Inspection.inspection_status).join(models.User, models.Project.user_id == models.User.id).join(models.Inspection, models.Project.id == models.Inspection.project_id).filter(models.User.id == session["user_id"]).order_by(models.Project.p_type.asc()).all()

    return render_template("portfolio/summary.html", projects=projects)


@bp.route("/portfolio/project/<int:project_id>")
@login_required
def project_details(project_id):

    db = get_db()
    print(project_id)

    project = db.query(models.Project.p_type, models.Project.po_number, models.Project.address, models.Project.num_chargers, models.Project.permit_num, models.Project.project_status, models.Project.start_date, models.Project.invoice, models.Project.datto, models.Inspection.i_type, models.Inspection.inspection_status, models.Inspection.inspection_date).join(models.User, models.Project.user_id == models.User.id).join(models.Inspection, models.Project.id == models.Inspection.project_id).filter(models.User.id == session["user_id"], models.Project.id == project_id).distinct().all()

    return render_template("portfolio/project_details.html", project=project, project_id=project_id)



