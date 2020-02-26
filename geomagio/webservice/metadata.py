from __future__ import absolute_import

import datetime
from .database import db


# known category values as constants
CATEGORY_FLAG = "flag"
CATEGORY_ADJUSTED_MATRIX = "adjusted-matrix"


class Metadata(db.Model):
    """Metadata database model.

    This class is used for Data flagging and other Metadata.

    Flag example:
    ```
    automatic_flag = Metadata(
        created_by = 'algorithm/version',
        start_time = UTCDateTime('2020-01-02T00:17:00.1Z'),
        end_time = UTCDateTime('2020-01-02T00:17:00.1Z'),
        network = 'NT',
        station = 'BOU',
        channel = 'BEU',
        category = CATEGORY_FLAG,
        comment = "spike detected",
        priority = 1,
        data_valid = False)
    ```

    Adjusted Matrix example:
    ```
    adjusted_matrix = Metadata(
        created_by = 'algorithm/version',
        start_time = UTCDateTime('2020-01-02T00:17:00Z'),
        end_time = None,
        network = 'NT',
        station = 'BOU',
        category = CATEGORY_ADJUSTED_MATRIX,
        comment = 'automatic adjusted matrix',
        priority = 1,
        value = {
            'parameters': {'x': 1, 'y': 2, 'z': 3}
            'matrix': [ ... ]
        }
    )
    ```
    """

    # table and primary key
    __tablename__ = "metadata"
    id = db.Column(db.Integer, primary_key=True)

    # author
    created_by = db.Column(db.Text, index=True)  # email/program id
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # time range
    start_time = db.Column(db.DateTime, index=True, nullable=True)
    end_time = db.Column(db.DateTime, index=True, nullable=True)
    # data this metadata applies to
    # channel/location nullable for wildcard
    network = db.Column(db.Text, index=True, nullable=False)
    station = db.Column(db.Text, index=True, nullable=False)
    channel = db.Column(db.Text, index=True, nullable=True)
    location = db.Column(db.Text, index=True, nullable=True)

    # metadata
    # category (flag, matrix, etc)
    category = db.Column(db.Text, index=True, nullable=False)
    # comment
    comment = db.Column(db.Text, nullable=True)
    # higher priority overrides lower priority
    priority = db.Column(db.Integer, default=1, index=True)
    # whether data is valid during
    data_valid = db.Column(db.Boolean, default=True, index=True)
    # json encoded value
    value = db.Column(db.JSON, nullable=False)

    # reviewer
    # email
    reviewed_by = db.Column(db.Text)
    # when reviewed
    reviewed_time = db.Column(db.DateTime)
    # comments by reviewer
    review_comment = db.Column(db.Text)
    # whether data rejected during review
    review_reject = db.Column(db.Boolean, default=False, index=True)
