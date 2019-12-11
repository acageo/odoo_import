import logging
import boto3
import json
import saboo
import io
import pandas as pd

_logger = logging.getLogger(__name__)

class OdooImport(object):

	def __init__(self,conf):
		self.conf = conf

	def import_pricelist(self,file,file_metadata):
		_logger.info("import bucket %s",file_metadata)
		try:
			if not 'joblogid' in file_metadata or not 'name' in file_metadata or not 'company' in file_metadata:
				_logger.error("Error in file_metadata %s",file_metadata)
				return {'message':"Error -- Could not find file_metadata in file"}
			else:
				saboo.client._init_odoo(self.conf)
				xls = saboo.PricelistXLS(self.conf)
				return xls.handle_request(io.BytesIO(file),file_metadata['name'],file_metadata['company'],file_metadata['joblogid'])
		except Exception as e:
			_logger.error("Exception in import process",e)
			return {'error':'Could Not Load file from S3'}

	def import_sale_data(self,file,file_metadata):
		_logger.info("import bucket %s",file_metadata)
		status = 'success'
		result = []
		task = saboo.api.PriceListJobApi(self.conf)
		if not 'joblogid' in file_metadata or not 'company' in file_metadata:
			_logger.error("Error in metadata %s",file_metadata)
			return {'message':"Error -- Invalid file metadata"}
		else:
			saboo.client._init_odoo(self.conf)
			odoo = saboo.tools.login(self.conf)
			xlsx = pd.ExcelFile(io.BytesIO(file))
			sb = pd.read_excel(xlsx,sheet_name=None)
			_logger.debug("The total number of sheets in file %s",sb.keys())
			for sheet in sb:
				sheet_result={}
				try:
					_logger.info("----- Started Processing Sheet %s",sheet)
					xls = saboo.XLS(self.conf)
					result_val = xls.handle_request(sb[sheet],file_metadata['company'],file_metadata['joblogid'])
					sheet_result.update({'status':'success','message':result_val})
				except Exception as e:
					_logger.error("Exception in import process",e)
					sheet_result.update({'status':'error'})
				_logger.info("----- Finished Processing Sheet %s",sheet)
		task.finishJob(file_metadata['joblogid'], status)
		return result


