from ddgs import DDGS

def web_search_node(state):
    question = state.get("question", "")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(question, max_results=3))
            
        web_context = "\n".join([f"{res['title']}: {res['body']}" for res in results])
        web_sources = [{"source": res["href"], "page": "Web"} for res in results]
        
        current_context = state.get("context", "")
        current_sources = state.get("sources", [])
        
        if current_context.strip():
            new_context = current_context + "\n\nWeb Search Results:\n" + web_context
            search_source = "Both"
        else:
            new_context = web_context
            search_source = "Web Search"
            
        return {
            **state,
            "context": new_context,
            "sources": current_sources + web_sources,
            "search_source": search_source
        }
    except Exception as e:
        print(f"Web search failed: {e}")
        return state
