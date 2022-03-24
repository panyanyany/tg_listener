from pympler.tracker import SummaryTracker

from scripts import listen_chain

tr = SummaryTracker()
try:
    listen_chain.main()
except:
    pass
tr.print_diff()
