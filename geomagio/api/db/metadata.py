import datetime
import enum

import orm


from .common import database, sqlalchemy_metadata


# known category values as enumeration
class MetadataCategory(str, enum.Enum):
    ADJUSTED_MATRIX = "adjusted-matrix"
    FLAG = "flag"
    READING = "reading"


class Metadata(orm.Model):
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

    __tablename__ = "metadata"
    __database__ = database
    __metadata__ = sqlalchemy_metadata

    id = orm.Integer(primary_key=True)

    # author
    created_by = orm.Text(index=True)
    created_time = orm.DateTime(default=datetime.datetime.utcnow, index=True)
    # reviewer
    reviewed_by = orm.Text(allow_null=True, index=True)
    reviewed_time = orm.DateTime(allow_null=True, index=True)

    # time range
    starttime = orm.DateTime(allow_null=True, index=True)
    endtime = orm.DateTime(allow_null=True, index=True)
    # what metadata applies to
    # channel/location allow_null for wildcard
    network = orm.String(index=True, max_length=255)
    station = orm.String(index=True, max_length=255)
    channel = orm.String(allow_null=True, index=True, max_length=255)
    location = orm.String(allow_null=True, index=True, max_length=255)

    # category (flag, matrix, etc)
    category = orm.String(index=True, max_length=255)
    # higher priority overrides lower priority
    priority = orm.Integer(default=1, index=True)
    # whether data is valid (primarily for flags)
    data_valid = orm.Boolean(default=True, index=True)
    # value
    metadata = orm.JSON(allow_null=True)
    # whether metadata is valid (based on review)
    metadata_valid = orm.Boolean(default=True, index=True)

    # general comment
    comment = orm.Text(allow_null=True)
    # review specific comment
    review_comment = orm.Text(allow_null=True)
