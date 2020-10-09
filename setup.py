from setuptools import setup, find_namespace_packages # type: ignore


def main() -> None:
    subpackages = find_namespace_packages('src')
    setup(
        name='HPI-overlay',
        zip_safe=False,

        packages=subpackages,
        package_dir={'': 'src'},
        # todo py.typed? not sure if need considering it's meant to be editable?
    )


if __name__ == '__main__':
    main()
