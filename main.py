from website import create_app

app = create_app()

if __name__ == '__main__': # Significa que só se rodarmos o file __name__, não se importarmos o mesmo, o programa executará o app.run().
    app.run(debug=True)
