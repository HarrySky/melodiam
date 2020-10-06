def main() -> None:
    import uvicorn  # type: ignore[import]

    from melodiam import conf
    from melodiam.auth import api

    uvicorn.run(
        api,
        host=conf.AUTH_LISTEN_HOST,
        port=conf.AUTH_LISTEN_PORT,
        loop="uvloop",
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
