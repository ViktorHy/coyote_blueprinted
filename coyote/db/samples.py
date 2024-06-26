import pymongo
from flask import current_app as app


class SampleHandler:
    def get_samples(self, user_groups: list = [], report: bool = False, search_str: str = ""):
        query = {"groups": {"$in": user_groups}}
        if report:
            query["report_num"] = {"$gt": 0}
        else:
            query["$or"] = [{"report_num": {"$exists": False}}, {"report_num": 0}]

        app.logger.info(f"this is my search string: {search_str}")
        if len(search_str) > 0:
            query["name"] = {"$regex": search_str}
        app.logger.info(query)
        samples = self.samples_collection.find(query).sort("time_added", -1)
        return samples

    def get_num_samples(self, sample_id: str) -> int:
        gt = self.samples_collection.find_one({"SAMPLE_ID": sample_id}, {"GT": 1})
        if gt:
            return len(gt.get("GT"))
        else:
            return 0

    def get_sample(self, name: str):
        """
        get sample by name
        """
        sample = self.samples_collection.find_one({"name": name})
        return sample

    def get_sample_ids(self, sample_id: str):
        a_var = self.samples_collection.find_one({"SAMPLE_ID": sample_id}, {"GT": 1})
        ids = {}
        if a_var:
            for gt in a_var["GT"]:
                ids[gt.get("type")] = gt.get("sample")
        return ids

    def reset_sample_settings(self, sample_id: str, settings):
        """
        reset sample to default settings
        """
        self.samples_collection.update(
            {"name": sample_id},
            {
                "$set": {
                    "filter_max_freq": settings["default_max_freq"],
                    "filter_min_freq": settings["default_min_freq"],
                    "filter_min_depth": settings["default_mindepth"],
                    "filter_min_reads": settings["default_min_reads"],
                    "filter_min_spanreads": settings["default_spanreads"],
                    "filter_min_spanpairs": settings["default_spanpairs"],
                    "checked_csq": settings["default_checked_conseq"],
                    "checked_genelists": settings["default_checked_genelists"],
                    "filter_max_popfreq": settings["default_popfreq"],
                    "checked_fusionlists": settings["default_checked_fusionlists"],
                    "min_cnv_size": settings["default_min_cnv_size"],
                    "max_cnv_size": settings["default_max_cnv_size"],
                    "checked_cnveffects": settings["default_checked_cnveffects"],
                }
            },
        )

    def update_sample_settings(self, sample_str, form):
        """
        update sample settings according to form data
        """
        checked_conseq = {}
        checked_genelists = {}
        checked_fusionlists = {}
        checked_fusioneffects = {}
        checked_fusioncallers = {}
        checked_cnveffects = {}
        for fieldname, value in form.data.items():
            if value == True:
                if fieldname.startswith("genelist"):
                    checked_genelists[fieldname] = 1
                elif fieldname.startswith("fusionlist"):
                    checked_fusionlists[fieldname] = 1
                elif fieldname.startswith(
                    "fusioncaller"
                ):  # donot change to fusioncallers, make it singular
                    checked_fusioncallers[fieldname] = 1
                elif fieldname.startswith("fusioneffect"):
                    checked_fusioneffects[fieldname] = 1
                elif fieldname.startswith("cnveffect"):
                    checked_cnveffects[fieldname] = 1
                else:
                    checked_conseq[fieldname] = 1

        self.samples_collection.update(
            {"name": sample_str},
            {
                "$set": {
                    "filter_max_freq": form.max_freq.data,
                    "filter_min_freq": form.min_freq.data,
                    "filter_min_depth": form.min_depth.data,
                    "filter_min_reads": form.min_reads.data,
                    "filter_min_spanreads": form.min_spanreads.data,
                    "filter_min_spanpairs": form.min_spanpairs.data,
                    "checked_csq": checked_conseq,
                    "checked_genelists": checked_genelists,
                    "filter_max_popfreq": form.max_popfreq.data,
                    "checked_fusionlists": checked_fusionlists,
                    "checked_fusioneffects": checked_fusioneffects,
                    "checked_fusioncallers": checked_fusioncallers,
                    "min_cnv_size": form.min_cnv_size.data,
                    "max_cnv_size": form.max_cnv_size.data,
                    "checked_cnveffects": checked_cnveffects,
                }
            },
        )
