# -*- coding: utf-8 -*-
class AppState:
    def __init__(self):
        self.download_mode   = None
        self.gbif_user       = None
        self.gbif_pass       = None
        self.gbif_email      = None
        self.gbif_dl_format  = "SIMPLE_CSV"
        self.taxon_key       = None
        self.taxon_name      = None
        self.taxon_rank      = None
        self.taxon_data      = None
        self.query_params    = {
            "basis_of_record"   : [],
            "exclude_inat"      : False,
            "year_from"         : None,
            "year_to"           : None,
            "accuracy"          : None,
            "coords_only"       : True,
            "no_geo_issues"     : True,
            "max_records"       : 10000,
            "exclude_datasets"  : [],
        }
        self.roi_geom        = None
        self.roi_source      = None
        self.roi_crs         = None
        self.results_gdf     = None
        self.results_taxon   = None
    def reset(self):
        self.__init__()
    def is_ready_for_download(self):
        return len(self.validate()) == 0
    def validate(self):
        errors = []
        if self.download_mode is None:
            errors.append("error_no_mode")
        if self.download_mode == "B":
            if not self.gbif_user:
                errors.append("error_no_credentials")
        if self.taxon_key is None:
            errors.append("error_no_taxon")
        if self.roi_geom is None:
            errors.append("error_no_roi")
        return errors
