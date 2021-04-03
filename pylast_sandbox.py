import pylast

API_KEY = "194ebdf5b49fa996adb5ffb9bfcab1db"
API_SECRET = "8e8cdae1a4bbd33ed6810e99a483e54c"

user = "EliosLastF_ck"
password = pylast.md5("G95y@uC3%E8L6X")


def main():
    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=user,
        password_hash=password
    )

    album = network.get_album(title="Chop Suey!", artist="System of a Down")
    tags = album.get_top_tags(limit=-1)
    for tag in tags:
        print(tag)



if __name__ == '__main__':
    main()

