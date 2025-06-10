import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

# --- データ構造の定義 ---
@dataclass
class Team:
    """チーム情報を格納するクラスです"""
    id: int
    name: str
    region: str

@dataclass
class League:
    """リーグ情報を格納するクラスです"""
    name: str
    teams: List[Team] = field(default_factory=list)
    matches: List[Tuple[Team, Team]] = field(default_factory=list)

# --- 設定値 ---
# 地域ごとのチーム数
REGION_DEFINITIONS = {
    'A': 2, 'B': 1, 'C': 2, 'D': 6, 'E': 1, 'F': 1, 'G': 5
}
# リーグごとのチーム数
LEAGUE_SIZES = [6, 4, 4, 4]
# 各チームの試合数
MATCHES_PER_TEAM = 3

def create_teams() -> List[Team]:
    """設定に基づいて全チームのリストを生成します"""
    teams = []
    team_id_counter = 1
    for region, count in REGION_DEFINITIONS.items():
        for i in range(1, count + 1):
            teams.append(Team(id=team_id_counter, name=f'チーム{region}-{i}', region=region))
            team_id_counter += 1
    return teams

def divide_into_leagues(teams: List[Team], league_sizes: List[int]) -> Optional[List[League]]:
    """
    チームを各リーグに割り振ります。
    地域がなるべく分散するように工夫しています。
    """
    leagues = [League(name=f'リーグ{i+1}') for i in range(len(league_sizes))]
    shuffled_teams = random.sample(teams, len(teams))

    for team in shuffled_teams:
        # チームを割り振るリーグ候補を探します
        available_leagues = []
        for i, league in enumerate(leagues):
            if len(league.teams) < league_sizes[i]:
                available_leagues.append(league)

        if not available_leagues:
            # 本来ここには来ないはずですが、念のため
            print("エラー: チームを割り振れるリーグがありません。")
            return None

        # 候補の中から、同じ地域のチームが最も少ないリーグを選びます
        best_leagues = sorted(
            available_leagues,
            key=lambda lg: sum(1 for t in lg.teams if t.region == team.region)
        )
        
        # 最も条件の良いリーグ（同じ地域のチームがいない、または最も少ない）に割り振ります
        min_region_count = sum(1 for t in best_leagues[0].teams if t.region == team.region)
        best_options = [lg for lg in best_leagues if sum(1 for t in lg.teams if t.region == team.region) == min_region_count]
        
        chosen_league = random.choice(best_options)
        chosen_league.teams.append(team)
        
    return leagues

def generate_matches_for_league(league: League, num_matches_per_team: int) -> bool:
    """バックトラッキングを使って、リーグ内の対戦カードを生成します"""
    
    teams = league.teams
    # 対戦可能なペアのリストを作成（同じ地域は除く）
    possible_pairs = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            if teams[i].region != teams[j].region:
                possible_pairs.append(tuple(sorted((teams[i], teams[j]), key=lambda t: t.id)))
    
    random.shuffle(possible_pairs)

    # 再帰的に対戦を探すヘルパー関数
    def _find_matches_recursive(
        matches: List[Tuple[Team, Team]],
        match_counts: Dict[int, int],
        pair_idx: int
    ) -> bool:
        # 全チームの試合数が条件を満たしたら成功
        if all(count == num_matches_per_team for count in match_counts.values()):
            league.matches = matches
            return True
        
        # 試すペアがなくなったら失敗
        if pair_idx >= len(possible_pairs):
            return False

        # --- 現在のペアを対戦させる場合 ---
        team1, team2 = possible_pairs[pair_idx]
        if match_counts[team1.id] < num_matches_per_team and match_counts[team2.id] < num_matches_per_team:
            # 対戦を追加して、再帰呼び出し
            new_matches = matches + [(team1, team2)]
            new_counts = match_counts.copy()
            new_counts[team1.id] += 1
            new_counts[team2.id] += 1
            if _find_matches_recursive(new_matches, new_counts, pair_idx + 1):
                return True

        # --- 現在のペアを対戦させない場合（スキップして次へ） ---
        if _find_matches_recursive(matches, match_counts, pair_idx + 1):
            return True

        return False

    initial_match_counts = {team.id: 0 for team in teams}
    return _find_matches_recursive([], initial_match_counts, 0)

def main():
    """メイン処理です"""
    print("リーグの組み分けを開始しますね！")

    # 成功するまで試行を繰り返します
    attempt_count = 0
    while True:
        attempt_count += 1
        print(f"\n--- 試行 {attempt_count}回目 ---")

        # 1. チームを生成
        all_teams = create_teams()

        # 2. リーグ分け
        print("リーグ分けを試みています...")
        leagues = divide_into_leagues(all_teams, LEAGUE_SIZES)
        if leagues is None:
            print("リーグ分けに失敗しました。リトライします。")
            continue

        # 3. 各リーグで対戦カードを作成
        all_leagues_ok = True
        for league in leagues:
            print(f"{league.name}の対戦カードを作成中...")
            if not generate_matches_for_league(league, MATCHES_PER_TEAM):
                print(f"{league.name}で条件に合う対戦が見つかりませんでした。")
                all_leagues_ok = False
                break
        
        # 4. 成功したら結果を表示して終了
        if all_leagues_ok:
            print("\nやったー！ 最高の組み合わせが見つかりました！")
            print("========================================")
            for league in leagues:
                print(f"\n【{league.name}】 (計{len(league.teams)}チーム)")
                # チーム一覧をID順にソートして表示
                sorted_teams = sorted(league.teams, key=lambda t: t.id)
                print("  [所属チーム]")
                for team in sorted_teams:
                    print(f"    - {team.name} (地域: {team.region})")
                
                print("  [対戦カード]")
                # 対戦カードをID順にソートして表示
                sorted_matches = sorted(league.matches, key=lambda m: (m[0].id, m[1].id))
                for t1, t2 in sorted_matches:
                    print(f"    - {t1.name} vs {t2.name}")
            print("========================================")
            break
        else:
            print("組み合わせが見つからなかったので、リーグ分けからやり直しますね！")


if __name__ == '__main__':
    main()