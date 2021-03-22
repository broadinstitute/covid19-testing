import argparse
import collections
import json
import pprint

from flask import Flask, render_template

app = Flask(__name__, template_folder=".")

DATA_JSON_PATH = "data.json"
TEMPLATE_PATH = "main_page_template.html"
DAILY_TEMPLATE_PATH = "daily_page_template.html"

CATEGORY_MAP = {
    "INCONCLUSIVE": "inconclusive",
    "NEG": "negative",
    "POS": "positive",
    "INVALID": "inconclusive"
}

def compute_template_args():
    with open(DATA_JSON_PATH, "rt") as f:
        data = json.load(f)

    counts_by_day = collections.defaultdict(lambda: collections.defaultdict(int))
    for entry in data['results']:
        day = entry['day']
        category = entry['result']
        try:
            category = CATEGORY_MAP[category]
        except KeyError as e:
            print("WARNING: unknown cateory: " + str(category) + " in entry: " + str(entry))
            continue

        counts_by_day[day][category] += entry['count']
        if entry['locale'] == "MA":
            counts_by_day[day]['samplesFromMA' ] += entry['count']
        elif entry['locale'] == "Non-MA":
            counts_by_day[day]['samplesFromOutOfState'] += entry['count']

        # note the pool count also only includes POSITIVES, NEGATIVES, INCONCLUSIVES, AND INVALIDS
        if 'pooled_samples' in entry:
            # counts total number of pooled samples
            counts_by_day[day]['total_pooled_samples'] += entry['pooled_samples']
            if category == 'positive':
                counts_by_day[day]['total_pooled_positives'] += entry['pooled_samples']

        if 'pool_size' in entry:
            # counts total number of individuals tested via pooling (swab count by tube)
            counts_by_day[day]['total_pooled_individuals'] += entry['pool_size']

    entries_by_day = []
    total_completed = 0
    total_positive = 0
    total_inconclusive = 0
    total_from_MA = 0
    total_from_out_of_state = 0
    total_pooled_samples = 0
    total_pooled_individuals = 0
    total_pooled_positives = 0

    for day, counters in counts_by_day.items():
        if day == '2020-03-23' or day == '2020-03-24': #  or day == datetime.datetime.now().strftime("%Y-%m-%d"):
            continue

        dateTokens = day.split("-")
        shortDate = str(int(dateTokens[1])) + "/" +str(int(dateTokens[2]))
        total_completed += counters['positive'] + counters['negative'] + counters['inconclusive']
        total_positive += counters['positive']
        total_inconclusive += counters['inconclusive']
        total_from_MA += counters['samplesFromMA']
        total_from_out_of_state += counters['samplesFromOutOfState']
        total_pooled_samples += counters['total_pooled_samples']
        total_pooled_individuals += counters['total_pooled_individuals']
        total_pooled_positives += counters['total_pooled_positives']

        entries_by_day.append({
            'day': day,
            'positive': counters['positive'],
            'negative': counters['negative'],
            'inconclusive': counters['inconclusive'],
            'shortDate': shortDate,
            'samplesPooled': counters['total_pooled_samples'],
            'individualsPooled': counters['total_pooled_individuals'],
            'poolPositives': counters['total_pooled_positives']
            #'samplesFromMA': counters['samplesFromMA'],
            #'samplesFromOutOfState': counters['samplesFromOutOfState'],
        })

    entries_by_day.sort(key=lambda x: x['day'])

    total_positive_percent = int(round((100.0 * total_positive) / total_completed))
    total_inconclusive_percent = "%0.1f" % round((100.0 * total_inconclusive) / total_completed, 1)
    total_from_MA_percent = int(round((100.0 * total_from_MA) / total_completed))
    total_from_out_of_state_percent = int(round((100.0 * total_from_out_of_state) / total_completed))
    result = {
        'DATA': entries_by_day,
        'TOTAL_COMPLETED': f"{total_completed:,}",
        'TOTAL_POSITIVE': f"{total_positive:,}",
        'TOTAL_POSITIVE_PERCENT':  total_positive_percent,
        'TOTAL_INCONCLUSIVE': f"{total_inconclusive:,}",
        'TOTAL_INCONCLUSIVE_PERCENT': total_inconclusive_percent,
        'TOTAL_FROM_MA': f"{total_from_MA:,}",
        'TOTAL_FROM_MA_PERCENT': total_from_MA_percent,
        'TOTAL_FROM_OUT_OF_STATE': f"{total_from_out_of_state:,}",
        'TOTAL_FROM_OUT_OF_STATE_PERCENT': total_from_out_of_state_percent,
        'TOTAL_POOLED': total_pooled_samples,
        'TOTAL_INDIVIDUALS_POOLED': total_pooled_individuals,
        'TOTAL_POOLED_POSITIVES': total_pooled_positives
    }

    #with open("daily_counts.json", "wt") as f:
    #    json.dump(entries_by_day, f)

    pprint.pprint(result)

    return result


@app.route("/")
def index():
    template_args = compute_template_args()
    return render_template(TEMPLATE_PATH, **template_args)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dev", action="store_true", help="Dev mode. Starts a server on localhost for viewing the template.")
    args = p.parse_args()

    if args.dev:
        app.run(debug=True)
        return

    template_args = compute_template_args()

    with app.app_context():
        with open("index.html", "wt") as f:
            f.write(render_template(TEMPLATE_PATH, **template_args))
        with open("daily/index.html", "wt") as f:
            f.write(render_template(DAILY_TEMPLATE_PATH, **template_args))


if __name__ == "__main__":
    main()
