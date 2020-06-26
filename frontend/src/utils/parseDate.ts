const parseDate = (date: string) => {
    const postAt = new Date(date);
    const offset = new Date().getTimezoneOffset();
    const elapsed =
        new Date(Date.now()).getTime() - postAt.getTime() + offset * 60000;
    if (elapsed < 60 * 1000) {
        return `${Math.floor(elapsed / 1000)} 秒前`;
    }
    if (elapsed < 60 * 60 * 1000) {
        return `${Math.floor(elapsed / (60 * 1000))} 分前`;
    }
    if (elapsed < 24 * 60 * 60 * 1000) {
        return `${Math.floor(elapsed / (60 * 60 * 1000))} 時間前`;
    }
    const localdate = new Date(postAt.getTime() + offset * 60000);
    let d = "";
    if (localdate.getFullYear() !== new Date(Date.now()).getFullYear())
        d += `${localdate.getFullYear()}年 `;
    d += `${localdate.getMonth() + 1}月${localdate.getDate()}日`;
    return d;
}

export default parseDate;