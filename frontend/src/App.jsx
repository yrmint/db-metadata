import DatabaseList from "./components/Index";

const App = () => {
  return (
    <div className="App">
      <header className="AppHeader">
        <h1>Databases Statistics</h1>
      </header>
      <main>
        <DatabaseList />
      </main>
    </div>
  );
};

export default App;
