"""Inspect a third-party Graph-MFN implementation; no data or training."""
from pathlib import Path
import importlib.util,json,torch,argparse
from torch import nn
root=Path(__file__).parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,default=root/'MMSA',help='Path to the MMSA checkout at the stated commit')
args=parser.parse_args()
spec=importlib.util.spec_from_file_location('graph_impl',args.repo/'src/MMSA/models/singleTask/Graph_MFN.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
torch.manual_seed(8)
net=module.DynamicFusionGraph(nn.Sequential(nn.Linear(5,3)),[2,2,2],3,nn.Sequential(nn.Linear(5,3)),torch.device('cpu'))
registered={id(p) for p in net.parameters()}
internal=[p for m in net.networks.values() for p in m.parameters()]
with torch.no_grad():
 net.efficacy_model[-1].weight.zero_()
 net.efficacy_model[-1].bias.fill_(2.)
 output,nodes,gates=net([torch.ones(2,2) for _ in range(3)])
report={'source':'thuiar/MMSA','commit':'a94e65d07fa1ae0d44e552390074b29b0898edfd','teaching_probe':True,'data_or_training_used':False,'edge_count':net.total_input_efficacies,'output_shape':list(output.shape),'internal_parameter_tensors':len(internal),'internal_parameter_tensors_registered':sum(id(p) in registered for p in internal),'controlled_final_bias':2.,'gate_min':float(gates.min()),'gate_max':float(gates.max())}
assert report['edge_count']==19 and report['internal_parameter_tensors_registered']==0
assert report['gate_min']==report['gate_max']==2.
(root/'graph_probe_results.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
