import os

from pykml import parser
from models import Area, Base, GeoPoint, Kataster, User, get_engine, get_session

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'vajnar')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'AldebaraN7#')
DB_NAME = os.getenv('DB_NAME', 'vajnar_globe')

def migrate():
    """Create any tables missing from the configured database."""
    engine = get_engine(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    Base.metadata.create_all(engine, checkfirst=True)
    build_db()

def build_db():
    kataster = "GOZD (2170)"
    email = "vajnar7@gmail.com"
    directory = "./kml"

    session = get_session()

    user = session.query(User).filter_by(email=email).one_or_none()
    if user is None:
        user = User(email=email, logged_in=False)
        session.add(user)
        session.commit()

    for file in os.listdir(directory):
        area_name = file.split('.kml')[0].split('-')
        area_name = area_name[0] + '/' + area_name[1]
        file = os.path.join(directory, file)
        with open(file, 'r', encoding="utf-8") as f:
            root = parser.parse(f).getroot()


        # define kataster object
        k = session.query(Kataster).filter_by(name=kataster).one_or_none()
        if k is None:
            k = Kataster(name=kataster, country="Slovenija", custom=False)
            session.add(k)
            session.commit()

        # define area object
        a = session.query(Area).filter_by(name=area_name, kataster=k).one_or_none()
        if a is None:
            a = Area(name=area_name, kataster=k)
            session.add(a)
            session.commit()

        if a not in user.areas:
            user.areas.append(a)
            session.commit()

        res = root.Document.Placemark.Polygon.outerBoundaryIs.LinearRing.coordinates.text.strip().split(' ')
        stamp = 0
        print(res)
        for p in res:
            c = p.split(',')
            lon, lat = c[0], c[1]
            a.geopoints.append(
                GeoPoint(latitude=lat, longitude=lon, stamp=stamp)
            )
            stamp += 1

        session.commit()



if __name__ == '__main__':
    migrate()