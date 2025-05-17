try:
    from result.views import add_score
    print("Successfully imported add_score")
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc() 