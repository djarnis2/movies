import { useState, useEffect } from "react";
import { import_cast, import_bio, import_list } from "../services/api";
import "../css/Imports.css";

function Imports() {
    const [listQuery, setListQuery] = useState("");
    const [listLimitQuery, setListLimitQuery] = useState("0");

    const [castQuery, setCastQuery] = useState("10");
    const [movieLimitQuery, setMovieLimitQuery] = useState("50");
    const [bioQuery, setBioQuery] = useState("50");

    const [loadingList, setLoadingList] = useState(false);
    const [loadingCast, setLoadingCast] = useState(false);
    const [loadingBio, setLoadingBio] = useState(false);

    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const isBusy = loadingList || loadingCast || loadingBio;
    const [startedAt, setStartedAt] = useState(null);
    const [elapsed, setElapsed] = useState(0);

    const startTimer = () => {
        setStartedAt(Date.now());
        setElapsed(0);
    };

    const stopTimer = () => {
        setStartedAt(null);
    };

    const runningLabel =
        loadingList ? "List" :
            loadingCast ? "Cast" :
                loadingBio ? "Bios" :
                    "Idle";



    useEffect(() => {
        if (!startedAt) return;
        const t = setInterval(() => {
            setElapsed(Math.floor((Date.now() - startedAt) / 1000));
        }, 1000);
        return () => clearInterval(t);
    }, [startedAt]);


    const handleCastImports = async (e) => {
        e.preventDefault();
        setError("");
        setResult(null)

        const movieLimit = Number(movieLimitQuery);
        const castLimit = Number(castQuery);

        if (!Number.isFinite(castLimit) || castLimit <= 0) {
            setError("Must be a positive number");
            return;
        }
        if (!Number.isFinite(movieLimit) || movieLimit <= 0) {
            setError("Movie limit must be a positive number");
            return;
        }


        try {
            setLoadingCast(true);
            startTimer();
            const data = await import_cast(movieLimit, castLimit)
            setResult(data);
        } catch (err) {
            setError(String(err));
        } finally {
            setLoadingCast(false);
            stopTimer();
        }
    };

    const handleBioImports = async (e) => {
        e.preventDefault();
        setError("");
        setResult(null)

        const bioLimit = Number(bioQuery);

        if (!Number.isFinite(bioLimit) || bioLimit <= 0) {
            setError("Must be a positive number");
            return;
        }

        try {
            setLoadingBio(true);
            startTimer();
            const data = await import_bio(bioLimit)
            setResult(data);
        } catch (err) {
            setError(String(err));
        } finally {
            setLoadingBio(false);
            stopTimer();
        }
    };

    const handleMovieList = async (e) => {
        e.preventDefault();
        setError("");
        setResult(null);

        const limit = Number(listLimitQuery);

        if (!Number.isFinite(limit) || limit < 0) {
            setError("Limit must be 0 (no limit) or a positive number");
            return;
        }

        const listId = listQuery.trim() === "" ? undefined : Number(listQuery);

        if (listId !== undefined && (!Number.isFinite(listId) || listId <= 0)) {
            setError("List ID must be a positive number (or left blanc for default)");
            return;
        }
        try {
            setLoadingList(true);
            startTimer();
            const data = await import_list(listId, limit);
            setResult(data);
        } catch (err) {
            setError(String(err?.message || err));
        } finally {
            setLoadingList(false);
            stopTimer();
        }
    };




    return (
        <div className="imports">
            <h2 className="title">Import movies, cast and actor biographies</h2>
            <br />
            <br />


            <div className="import-container">

                <div className="list-container">
                    {/* LIST IMPORT */}
                    <div className="import-form">
                        <form className="form" onSubmit={handleMovieList}>
                            <div className="field">
                                <label htmlFor="list_num">TMDB List number</label>
                                <input type="number"
                                    placeholder="TMDB List or leave blanc for default"
                                    value={listQuery}
                                    onChange={(e) => setListQuery(e.target.value)}
                                />
                            </div>
                            <div className="field">
                                <label htmlFor="limit">Limit (number of movies)</label>
                                <input
                                    type="number"
                                    placeholder="Limit (0 = all)"
                                    value={listLimitQuery}
                                    onChange={(e) => setListLimitQuery(e.target.value)}
                                />
                            </div>
                            <button type="submit" disabled={isBusy || loadingList}>
                                {loadingList ? "Importing list..." : "Import List"}
                            </button>
                        </form>

                    </div>

                </div>




                <div className="cast-container ">
                    {/* CAST IMPORT */}
                    <div className="import-form">
                        <form className="form" onSubmit={handleCastImports}>
                            <div className="field">
                                <label htmlFor="movie-limt">Movies to process</label>
                                <input
                                    type="number"
                                    min="1"
                                    placeholder="Movies to process"
                                    value={movieLimitQuery}
                                    onChange={(e) => setMovieLimitQuery(e.target.value)}
                                />
                            </div>
                            <div className="field">
                                <label htmlFor="actors-per-movie">Actors per movie</label>
                                <input
                                    type="number"
                                    min="1"
                                    placeholder="Actors per movie"
                                    value={castQuery}
                                    onChange={(e) => setCastQuery(e.target.value)}
                                />
                            </div>
                            <button type="submit" disabled={isBusy || loadingCast}>
                                {loadingCast ? "Importing cast..." : "Import Cast"}
                            </button>
                        </form>
                    </div>


                </div>

                <div className="bio-container">
                    {/* BIO IMPORT */}
                    <div className="import-form">
                        <form className="form" onSubmit={handleBioImports}>
                            <div className="field">
                                <label htmlFor="bio-input">Actors to fetch biographies for</label>
                                <input
                                    type="number"
                                    min="1"
                                    placeholder="Actors to fetch biographies for"
                                    className="bio-input"
                                    value={bioQuery}
                                    onChange={(e) => setBioQuery(e.target.value)}
                                />
                            </div>
                            <button type="submit" disabled={isBusy || loadingBio}>
                                {loadingBio ? "Importing bios..." : "Import Bios"}
                            </button>

                        </form>
                    </div>

                </div>
            </div>
            <div className="output-container child">
                {/* OUTPUT */}
                {isBusy && (
                    <div style={{ marginTop: "0.75rem", color: "blue" }}>
                        <br />
                        <hr></hr>
                        <br />
                        <div><strong>Running:</strong> {runningLabel}</div>
                        <div><strong>Elapsed:</strong> {elapsed}s</div>
                    </div>
                )}
                {(loadingList || loadingCast || loadingBio) && (
                    <div style={{ marginTop: "1rem", opacity: 0.9, color: "green" }}>
                        <br />
                        <hr></hr>
                        <br />
                        <strong>Import running…</strong>
                        <div>This can take several minutes. Please keep this page open.</div>
                        <div>Output will appear when the import finishes.</div>
                    </div>
                )}

                {error && (<><br /><hr /><br /><p style={{ color: "salmon" }}>{error}</p></>)}

                {result && (
                    <div style={{ marginTop: "1rem" }}>
                        <br />
                        <hr></hr>
                        <br />
                        <div>ok: {String(result.ok)} (code: {result.code})</div>

                        {result.err && (
                            <>
                                <br />
                                <hr></hr>
                                <br />
                                <h4>stderr</h4>
                                <pre style={{ whiteSpace: "pre-wrap", color: "red" }}>{result.err}</pre>
                            </>
                        )}

                        {result.out && (
                            <>
                                <br />
                                <hr></hr>
                                <br />
                                <h4>stdout</h4>
                                <pre style={{ whiteSpace: "pre-wrap", color: "green" }}>{result.out}</pre>
                            </>
                        )}
                    </div>
                )}
            </div>




        </div>
    );
}

export default Imports;
