def main() -> None:
    import uvicorn  # type: ignore[import]

    from melodiam.auth import api

    uvicorn.run(api, host="0.0.0.0", port=7455, loop="uvloop", proxy_headers=True)


if __name__ == "__main__":
    main()
