# c3-web-query
Query or push data to C3

## Single Query of A Specific Submission

You may use default python interpreter or ipython interactive prompt to 
perform these commands. 106445 is the submission ID. Replace it by your own 
target:

```python
import c3.api.query as c3query

ci = c3query.configuration.get_instance()
ci.read_configuration('my_conf.ini')


from c3.api.api_utils import APIQuery

api = APIQuery(ci.config['C3']['URI'])
rparam = {"username": ci.config['C3']['URI'],"api_key": ci.config['C3']['APIKey']}

c3query.api_instance.set_api_params(api, rparam)


machine_report = c3query.query_specific_machine_report(106445)
```
