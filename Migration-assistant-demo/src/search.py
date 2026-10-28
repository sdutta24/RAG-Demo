def filter_migration_rules(rules,filters):
    filtered_rules = []
    filtered_index = []
    for index,rule in enumerate(rules):
        match = True

        for key, value in filters.items():
            if value is not None and rule.get(key) != value:
                match = False
                break
        if match:
            filtered_rules.append(rule)
            filtered_index.append(index)
    return filtered_rules, filtered_index

#def search_migration_rules(rules, embeddings, query_embedding):
    #results = []
    #for rule, embedding in zip(rules,embeddings):
        #sim_score = calculate_cosine_similarity(query_embedding,embedding)
        #results.append({
            #"id": rule["id"],
            #"title": rule["title"],
            #"rule": rule["rule"],
            #"score": float(sim_score)
        #})
    ##return results

#def ranked_results(results,top_k=3):
    #ranked = sorted(
        #results,
        #key = lambda x: x["score"],
        #reverse = True
    #)
    return ranked[:top_k]


    
       
        