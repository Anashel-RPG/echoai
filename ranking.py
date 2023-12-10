import os
from PIL import Image
from collections import Counter
import itertools
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Constants for directory names
GOOD_DIR = 'ranking_good'
BAD_DIR = 'ranking_bad'

def extract_metadata(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        return exif_data.get(0x0131), exif_data.get(0x010E)
    except Exception as e:
        print(f"Error reading metadata from {image_path}: {e}")
        return None, None

def process_text(text):
    return [phrase.strip().lower() for phrase in text.split(',')]

def ngram_analysis(phrases):
    vectorizer = CountVectorizer(ngram_range=(2, 3))
    ngrams = vectorizer.fit_transform(phrases)
    ngram_freq = Counter(zip(vectorizer.get_feature_names_out(), np.asarray(ngrams.sum(axis=0)).ravel()))
    return ngram_freq.most_common(5)  # This should return a list of tuples

def topic_modeling(phrases):
    vectorizer = CountVectorizer()
    data_vectorized = vectorizer.fit_transform(phrases)
    lda_model = LatentDirichletAllocation(n_components=3, learning_method='online')
    lda_model.fit(data_vectorized)
    topics = lda_model.components_
    terms = vectorizer.get_feature_names_out()
    topic_summaries = []
    for topic_idx, topic in enumerate(topics):
        topic_summaries.append(" ".join([terms[i] for i in topic.argsort()[:-5 - 1:-1]]))
    return topic_summaries

def analyze_directory(directory, exclude_phrases=set(), exclude_combinations=set(), exclude_ngrams=set()):
    phrase_freq = Counter()
    combination_freq = Counter()
    all_phrases = []

    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            artist, description = extract_metadata(os.path.join(directory, filename))
            if description:
                phrases = process_text(description)
                all_phrases.extend(phrases)
                phrase_freq.update(phrases)
                combinations = itertools.combinations(phrases, 2)
                combination_freq.update(combinations)

    # Perform n-gram analysis and convert it to a Counter
    ngram_freq_list = ngram_analysis(all_phrases)
    ngram_freq = Counter(dict(ngram_freq_list))

    # Remove excluded elements
    for phrase in exclude_phrases:
        if phrase in phrase_freq:
            del phrase_freq[phrase]
    for combination in exclude_combinations:
        if combination in combination_freq:
            del combination_freq[combination]
    for ngram in exclude_ngrams:
        if ngram in ngram_freq:
            del ngram_freq[ngram]

    # Sort and pick top 5, excluding the first entry
    top_phrases = [phrase for phrase, count in phrase_freq.most_common(6)[1:]]
    top_combinations = [combination for combination, count in combination_freq.most_common(6)[1:]]
    top_ngrams = [ngram for ngram, count in ngram_freq.most_common(6)[1:]]

    topics = topic_modeling(all_phrases)
    return phrase_freq, combination_freq, ngram_freq, topics, top_phrases, top_combinations, top_ngrams

def format_report(title, items, limit, is_topic=False, is_ngram=False):
    border = "=" * 50
    print(border)
    print(f"{title.center(50)}")
    print(border)
    for item in items[:limit]:
        if is_ngram:
            # Extracting n-gram string and its count
            ngram_tuple, count = item
            ngram_str = ngram_tuple[0]  # Only the N-Gram string
            print(f"{ngram_str:<40} {count:>8}")
        elif is_topic:
            # Topics are strings, print directly
            print(f"{item:<40}")
        elif isinstance(item, tuple):
            # For phrases and combinations
            phrase_comb_str = " + ".join(item[0]) if isinstance(item[0], tuple) else item[0]
            count = item[1]
            print(f"{phrase_comb_str:<40} {count:>8}")
        else:
            # For any other types
            print(f"{str(item):<40}")
    print(border)
    print()

def compare_directories(good_phrases, bad_phrases):
    overlap = set(good_phrases).intersection(set(bad_phrases))
    vectorizer = CountVectorizer()
    good_vec = vectorizer.fit_transform(good_phrases)
    bad_vec = vectorizer.transform(bad_phrases)
    similarity = cosine_similarity(good_vec, bad_vec)
    return overlap, similarity

def summarize_similarity_matrix(matrix):
    avg_similarity = np.mean(matrix)
    return f"Average Similarity: {avg_similarity:.2f}"

def analyze_sections(directory):
    max_sections = 0
    # First, determine the maximum number of sections
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            _, description = extract_metadata(os.path.join(directory, filename))
            if description:
                max_sections = max(max_sections, len(description.split(',')))

    section_counters = [Counter() for _ in range(max_sections)]

    for filename in os.listdir(directory):
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            _, description = extract_metadata(os.path.join(directory, filename))
            if description:
                sections = description.split(',')
                for i, section in enumerate(sections):
                    section = section.strip().lower()
                    if i == 0:
                        section = " ".join(section.split()[2:])
                    section_counters[i].update([section])

    return section_counters

def process_text_for_grouping(text):
    grouped_phrases = {}
    for phrase in text.split(','):
        words = phrase.strip().lower().split()
        if len(words) > 2:
            key = tuple(words[-2:])  # Use the last two words as the key
            grouped_phrases.setdefault(key, []).append(phrase)
    return grouped_phrases

def count_grouped_phrases(grouped_phrases):
    phrase_count = Counter()
    for key, phrases in grouped_phrases.items():
        phrase_count.update({key: len(phrases)})
    return phrase_count

def main():
    # Analyze Good Dataset
    good_data = analyze_directory(GOOD_DIR)
    good_phrase_freq, good_combination_freq, good_ngram_freq, good_topics, good_top_phrases, good_top_combinations, good_top_ngrams = good_data

    # Analyze sections for the Good Dataset
    good_section_counters = analyze_sections(GOOD_DIR)
    bad_section_counters = analyze_sections(BAD_DIR)  # Adding analysis for the Bad Dataset

    # Display top 5 phrases for each section in the good dataset
    for i, counter in enumerate(good_section_counters):
        title = f"Good Dataset - Section {i + 1} Top 5 Phrases"
        format_report(title, counter.most_common(5), 5)

    # Perform Grouped Phrase Analysis
    good_grouped_phrases = process_text_for_grouping(",".join(good_phrase_freq))
    good_phrase_count = count_grouped_phrases(good_grouped_phrases)
    # format_report("Good Dataset - Grouped Phrase Analysis", good_phrase_count.most_common(10), 10)

    # Extract Top 5 elements from Good Dataset
    top_good_phrases = set([item[0] for item in good_phrase_freq.most_common(5)])
    top_good_combinations = set([tuple(sorted(item[0])) for item in good_combination_freq.most_common(5)])
    top_good_ngrams = set([ngram[0] for ngram, _ in good_ngram_freq.items()])

    # Collect top 5 phrases from each section of the good dataset
    exclude_phrases_from_good = set()
    for section_counter in good_section_counters:
        top_phrases = [phrase for phrase, count in section_counter.most_common(5)]
        exclude_phrases_from_good.update(top_phrases)

    # Analyze Bad Dataset with exclusion of Top 5 Good elements
    bad_data = analyze_directory(BAD_DIR, exclude_phrases=top_good_phrases, exclude_combinations=top_good_combinations, exclude_ngrams=top_good_ngrams)
    bad_phrase_freq, bad_combination_freq, bad_ngram_freq, bad_topics, bad_top_phrases, bad_top_combinations, bad_top_ngrams = bad_data

    overlap, similarity = compare_directories(list(good_phrase_freq), list(bad_phrase_freq))

    # format_report("Good Dataset - Top 10 Prompt", good_phrase_freq.most_common(10), 10)
    # format_report("Good Dataset - Top 3 Combinations", good_combination_freq.most_common(3), 3)
    #format_report("Good Dataset - Top 5 N-Grams", list(good_ngram_freq.items()), 5, is_ngram=True)

    # Display top 5 phrases for each section in the bad dataset
    for i, counter in enumerate(bad_section_counters):
        title = f"Bad Dataset - Section {i+1} Top 5 Phrases"
        format_report(title, counter.most_common(5), 5)

    #format_report("Bad Dataset - Top 10 Prompt", bad_phrase_freq.most_common(10), 10)
    #format_report("Bad Dataset - Top 3 Combinations", bad_combination_freq.most_common(3), 3)
    # format_report("Bad Dataset - Topics", [(topic, '') for topic in bad_topics], 3, is_topic=True)

    # Limiting the overlap output to top 5
    print("Overlap:\n" + "\n".join(list(overlap)[:5]))
    print("\nSimilarity Summary:\n", summarize_similarity_matrix(similarity))

if __name__ == "__main__":
    main()