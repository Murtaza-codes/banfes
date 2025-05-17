try:
    from result.views_temp import add_score
    print("Successfully imported add_score from temp views")
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc() 